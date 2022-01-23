from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import column, expr, from_json, udf
from pyspark.sql.types import *
from pyspark.ml.classification import MultilayerPerceptronClassificationModel, MultilayerPerceptronClassifier
from kafka import KafkaProducer
import json
from pyhive import hive
import time
import random
import base64
import shutil
import os
from datetime import datetime


spark = SparkSession.builder.appName('BDAModel').getOrCreate()
spark.sparkContext.setLogLevel('WARN')
logger = spark.sparkContext._jvm.org.apache.log4j.LogManager.getLogger(
    __name__)

model = None
db_model_weights = None
for i in range(100):
    logger.warn(f'Attempting to connect for {i}th time to hive...')
    try:
        conn = hive.Connection(host='hive-server')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM modelweights ORDER BY ts DESC')
        row = cursor.fetchone()
        if row:
            # Index dependent on table schema
            weights_data = row[-1]
            archive_path = './db_model_weights.tar.gz'
            folder_path = './db_model_weights'
            with open(archive_path, 'wb+') as f:
                f.write(base64.b64decode(weights_data))
            shutil.unpack_archive(archive_path, folder_path)
            model = MultilayerPerceptronClassificationModel.load(folder_path)
            db_model_weights = model.weights
            shutil.rmtree(folder_path)
            os.remove(archive_path)
        logger.warn(f'Read model weights: {db_model_weights}')
        cursor.close()
        conn.close()
        break
    except Exception as ex:
        logger.error(f'{ex}')
        logger.warn('Connect failed. Trying again in 5 seconds...')
        time.sleep(5)

stream_schema = StructType([
    StructField('lon',          DoubleType(),       False),
    StructField('lat',          DoubleType(),       False),
    StructField('measured',     IntegerType(),      False),
    StructField('id',           StringType(),       False),
    StructField('ts',           TimestampType(),    False),
    StructField('kafkatopic',   StringType(),       False),
    StructField('aqi',          IntegerType(),      True),
    StructField('temp',         DoubleType(),       True),
    StructField('pressure',     DoubleType(),       True),
    StructField('humidity',     DoubleType(),       True),
    StructField('clouds',       IntegerType(),      True),
    StructField('windspeed',    DoubleType(),       True),
    StructField('winddeg',      DoubleType(),       True),
])


def aqi_category(aqi):
    if aqi <= 50:
        return 0  # Good
    if aqi <= 100:
        return 1  # Moderate
    if aqi <= 150:
        return 2  # Unhealthy for sensitive groups
    if aqi <= 200:
        return 3  # Unhealthy
    if aqi <= 300:
        return 4  # Very Unhrealthy
    return 5  # Hazardous


# TODO: Set initial offset to earliest
df = spark.readStream \
    .format('kafka') \
    .option('kafka.bootstrap.servers', 'kafka:9092') \
    .option('subscribe', 'spark') \
    .option('startingOffsets', 'earliest') \
    .load()

df_json = df \
    .select(from_json(df.value.cast('string'), stream_schema).alias('v')) \
    .select('v.*') \
    .withWatermark('ts', '20 seconds')

pollution_df = df_json \
    .filter(column('kafkatopic').startswith('pollution')) \
    .select('aqi', 'ts', 'kafkatopic', 'id') \
    .withColumnRenamed('id', 'pollutionid') \
    .alias('pollution')

weather_df = df_json \
    .filter(column('kafkatopic').startswith('weather')) \
    .select('lon', 'lat', 'temp', 'pressure', 'humidity', 'clouds', 'windspeed', 'winddeg', 'ts', 'kafkatopic', 'id') \
    .withColumnRenamed('id', 'weatherid') \
    .withColumn('weatherts', column('ts')) \
    .alias('weather')


weather_with_pollution = weather_df.join(
    pollution_df,
    expr("""
         REPLACE(weather.kafkatopic, 'weather', '') = REPLACE(pollution.kafkatopic, 'pollution', '')    AND
         weather.ts + interval 10 seconds > pollution.ts                                                AND
         weather.ts < pollution.ts + interval 10 seconds
    """),
    "inner")                                                        \
    .withColumn('city', udf(lambda s: s.replace('weather', ''), StringType())('weather.kafkatopic')) \
    .select('weather.*', 'pollution.*', 'city')  \
    .drop('ts', 'kafkatopic') \
    .withColumnRenamed('weatherts', 'ts')

input_cols = list(
    set(weather_with_pollution.columns) - set(['aqi', 'pollutionid', 'weatherid', 'city', 'ts']))
layers = [len(input_cols), 50, 6]
asm = VectorAssembler(inputCols=input_cols, outputCol='features')
weather_with_pollution = asm \
    .transform(weather_with_pollution) \
    .withColumn('label', udf(aqi_category, IntegerType())('aqi'))

kafka_producer = KafkaProducer(bootstrap_servers='kafka:9092')
trainer = MultilayerPerceptronClassifier(layers=layers)
if db_model_weights is not None:
    num_weights = sum(map(lambda p: (p[0]+1)*p[1], zip(layers, layers[1:])))
    if num_weights != len(db_model_weights):
        logger.warn('Weight data is outdated!')
        model = None
        db_model_weights = None


def train(batch: DataFrame, batchId):
    global model
    rows = batch.collect()
    random.shuffle(rows)
    for i, row in enumerate(rows):
        params = {trainer.initialWeights: db_model_weights}
        logger.warn(f'Processing row {i}/{len(rows)} of batch {batchId}')
        if model is not None:
            kafka_producer.send(f'modelpredictions{row.city}',
                                json.dumps({
                                    'prediction': int(model.predict(row.features)),
                                    'actual': row.label,
                                    'weatherid': row.weatherid,
                                    'pollutionid': row.pollutionid,
                                    'city': row.city,
                                    'ts': row.ts.strftime('%Y-%m-%d %H:%M:%S.%f'),
                                }).encode())
            params[trainer.initialWeights] = model.weights
        model = trainer.fit(spark.createDataFrame([row]), params=params)
        if i != 0 and i == 1 or random.randint(0, 100) == 0:
            fname = f'/models/model_{batchId}_{i}_{random.randint(0, 999999)}'
            logger.warn(f'Saving model data to {fname}')
            model.write().overwrite().save(fname)


weather_with_pollution.writeStream \
    .outputMode('append') \
    .trigger(processingTime='20 seconds') \
    .format('console') \
    .start()
weather_with_pollution.writeStream \
    .foreachBatch(train) \
    .start().awaitTermination()
