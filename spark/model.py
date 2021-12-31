from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import column, expr, from_json, udf
from pyspark.sql.types import *
from pyspark.ml.classification import MultilayerPerceptronClassifier
from kafka import KafkaProducer
import json

spark = SparkSession.builder.appName('BDAModel').getOrCreate()
spark.sparkContext.setLogLevel('WARN')
logger = spark.sparkContext._jvm.org.apache.log4j.LogManager.getLogger(
    __name__)

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
    if aqi < 300:
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
    .select('lon', 'lat', 'temp', 'pressure', 'humidity', 'clouds', 'windspeed', 'winddeg', 'ts', 'kafkatopic') \
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
    .drop('ts', 'kafkatopic')

layers = [len(weather_with_pollution.columns) - 1, 5, 6]
asm = VectorAssembler(inputCols=list(
    set(weather_with_pollution.columns) - set(['aqi'])), outputCol='features')
weather_with_pollution = asm            \
    .transform(weather_with_pollution)  \
    .withColumn('label', udf(aqi_category, IntegerType())('aqi'))

model = MultilayerPerceptronClassifier(layers=layers)
model_weights = None
kafka_producer = KafkaProducer(bootstrap_servers='kafka:9092')


def train(batch: DataFrame, batchId):
    global model, model_weights, layers
    if batch.count() <= 0:
        return
    # TODO: evaluate the model on batch and save the results to db or whatever for analysis
    model_weights = model.fit(batch).weights
    # TODO: Do this every nth batch maybe
    kafka_producer.send('modelweights', json.dumps(
        {'weights': model_weights.tolist()}).encode())
    model = MultilayerPerceptronClassifier(
        layers=layers, initialWeights=model_weights)
    logger.warn(f'{model_weights.tolist()}')


weather_with_pollution.writeStream  \
    .foreachBatch(train)            \
    .start().awaitTermination()


# weather_with_pollution.writeStream          \
#     .outputMode('append')                   \
#     .trigger(processingTime='20 seconds')   \
#     .format('console')                      \
#     .start()
