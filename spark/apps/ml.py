from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json,udf
from pyspark.sql.types import *
from datetime import timedelta
from pyspark.mllib.regression import LabeledPoint,StreamingLinearRegressionWithSGD
from pyspark.ml.feature import VectorAssembler

spark = SparkSession.builder.appName("LoggerApp").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

pollution_schema = StructType([
    StructField("aqi",IntegerType(),False),
    StructField("lon",DoubleType(),False),
    StructField("lat",DoubleType(),False),
    StructField("measured",IntegerType(),False),
    StructField("id",StringType(),False),
    StructField("ts",TimestampType(),False),
    StructField("kafkatopic",StringType(),False),
])

weather_schema = StructType([
    StructField("lon",DoubleType(),False),
    StructField("lat",DoubleType(),False),
    StructField("temp",DoubleType(),False),
    StructField("pressure",DoubleType(),False),
    StructField("humidity",DoubleType(),False),
    StructField("visibility",DoubleType(),False),
    StructField("windspeed",DoubleType(),False),
    StructField("winddeg",DoubleType(),False),
    StructField("measured",IntegerType(),False),
    StructField("id",StringType(),False),
    StructField("ts",TimestampType(),False),
    StructField("kafkatopic",StringType(),False),
])

df = spark.readStream.format("kafka").option("kafka.bootstrap.servers","kafka:9092").option("subscribe","spark").load()

pollution_df = df.filter(df.value.contains("pollution")).select(from_json(df.value.cast("string"),pollution_schema).alias("value")).select("value.*")
weather_df = df.filter(df.value.contains("weather")).select(from_json(df.value.cast("string"),weather_schema).alias("value")).select("value.*")

city_from_pollution_topic_udf = udf(lambda x:x.replace("pollution",""),StringType())
city_from_weather_topic_udf = udf(lambda x:x.replace("weather",""),StringType())

pollution_df = pollution_df.withColumn("city",city_from_pollution_topic_udf(pollution_df["kafkatopic"]))
weather_df = weather_df.withColumn("city",city_from_weather_topic_udf(weather_df["kafkatopic"]))

pollution_df = pollution_df.drop("lon","lat","measured","id","kafkatopic")
weather_df = weather_df.drop("lon","lat","measured","id","kafkatopic")

timestamp_from_datetime_udf = udf(lambda x:x.timestamp(),DoubleType())
pollution_df = pollution_df.withColumn("timestamp",timestamp_from_datetime_udf(pollution_df["ts"]))

cities_dict={"warsaw":0,"berlin":1,"delhi":2,"moscow":3}
city_idx_udf = udf(lambda x:cities_dict[x],IntegerType())
pollution_df = pollution_df.withColumn("city_idx",city_idx_udf(pollution_df["city"]))

start_time_udf = udf(lambda x:x-timedelta(seconds=10),TimestampType())
end_time_udf = udf(lambda x:x+timedelta(seconds=10),TimestampType())

weather_df = weather_df.withColumn("starttime",start_time_udf(weather_df["ts"]))
weather_df = weather_df.withColumn("endtime",end_time_udf(weather_df["ts"]))

df = pollution_df.join(weather_df,((pollution_df["city"] == weather_df["city"]) & (pollution_df["ts"].between(weather_df["starttime"],weather_df["endtime"]))),"inner")

df.writeStream.outputMode("append").trigger(processingTime="5 seconds").format("console").start()

features = [
    "temp",
    "pressure",
    "humidity",
    "visibility",
    "windspeed",
    "winddeg",
    "timestamp",
    "city_idx"
]

assembler = VectorAssembler(inputCols=features,outputCol="features")
df = assembler.transform(df)

model = StreamingLinearRegressionWithSGD(numIterations=10) # default step 0.1
model.setInitialWeights([0.0]*len(features))

train_data = df.map(lambda x:LabeledPoint(x.aqi,x.features))
model.trainOn(train_data)
predictions = model.predictOn(df.features)
