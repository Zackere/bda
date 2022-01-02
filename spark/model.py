from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession, Row
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import column, expr, from_json, udf
from pyspark.sql.types import *
from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline
from kafka import KafkaProducer
import json
from pyhive import hive
import time
import numpy as np



spark = SparkSession.builder.appName('BDAModel').getOrCreate()
spark.sparkContext.setLogLevel('WARN')
logger = spark.sparkContext._jvm.org.apache.log4j.LogManager.getLogger(
    __name__)

model_weights = None
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
            model_weights = json.loads(row[-1])
            assert isinstance(model_weights, list)
        logger.warn(f'Read model weights: {model_weights}')
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
df = spark.readStream                                   \
    .format('kafka')                                    \
    .option('kafka.bootstrap.servers', 'kafka:9092')    \
    .option('subscribe', 'spark')                       \
    .load()

df_json = df                                                                \
    .select(from_json(df.value.cast('string'), stream_schema).alias('v'))   \
    .select('v.*')                                                          \
    .withWatermark('ts', '20 seconds')

pollution_df = df_json                                                  \
    .filter(column('kafkatopic').startswith('pollution'))               \
    .select('aqi', 'ts', 'kafkatopic')                                  \
    .alias('pollution')

weather_df = df_json                                                                                            \
    .filter(column('kafkatopic').startswith('weather'))                                                         \
    .select('id','lon', 'lat', 'temp', 'pressure', 'humidity', 'clouds', 'windspeed', 'winddeg', 'ts', 'kafkatopic') \
    .alias('weather')


weather_with_pollution = weather_df.join(
    pollution_df,
    expr("""
         REPLACE(weather.kafkatopic, 'weather', '') = REPLACE(pollution.kafkatopic, 'pollution', '')    AND
         weather.ts + interval 10 seconds > pollution.ts                                                AND
         weather.ts < pollution.ts + interval 10 seconds
    """),
    "inner")                                \
    .select('weather.*', 'pollution.aqi')   \

layers = [len(weather_with_pollution.columns) - 4, 5, 6]
asm = VectorAssembler(inputCols=list(
    set(weather_with_pollution.columns) - set(['aqi','ts', 'kafkatopic', 'id'])), outputCol='features')
final_data = weather_with_pollution.withColumn('label', udf(aqi_category, IntegerType())('aqi'))

kafka_producer = KafkaProducer(bootstrap_servers='kafka:9092')
model = MultilayerPerceptronClassifier(layers=layers)
num_weights = sum(map(lambda p: (p[0]+1)*p[1], zip(layers, layers[1:])))
if model_weights and num_weights != len(model_weights):
    logger.warn('Weight data is outdated!')
    model_weights = None


def train(batch: DataFrame, batchId):
    if batch.count() <= 0:
        return
    global model_weights
    # TODO: evaluate the model on batch and save the results to db or whatever for analysis
    # params = {
    #     model.initialWeights: None if not model_weights else np.array(
    #         model_weights)
    # }

    batch.show()

    model.setInitialWeights(None if not model_weights else np.array(model_weights))

    pipeline = Pipeline(stages=[asm, model])

    mockModel = pipeline.fit(batch)
    result = mockModel.transform(batch)
    predictionAndLabels = result.select("prediction", "label")
    evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
    logger.warn(f'Accuracy: {str(evaluator.evaluate(predictionAndLabels))}')
    result.show()

    for jsonRow in result.toJSON().collect():
        kafka_producer.send('modelEvaluation', jsonRow.encode())

    # predictionData.foreach(lambda x: 
    #     kafka_producer.send('modelEvaluation', json.dumps(
    #     {'features': x['features'], 'prediction': x['prediciton'], 'label': x['label']}).encode())
    #     )

    model.setInitialWeights(None if not model_weights else np.array(model_weights))
    pipeline = Pipeline(stages=[asm, model])


    new_model = pipeline.fit(batch)
    model_weights = new_model.stages[-1].weights.tolist()
    # TODO: Do this every nth batch maybe
    kafka_producer.send('modelweights', json.dumps(
        {'weights': model_weights}).encode())
    logger.warn(f'{model_weights}')


# weather_with_pollution.writeStream          \
#     .outputMode('append')                   \
#     .trigger(processingTime='20 seconds')   \
#     .format('console')                      \
#     .start()

final_data.writeStream  \
    .foreachBatch(train)            \
    .start().awaitTermination()
