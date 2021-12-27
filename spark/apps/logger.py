from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import *

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

pollution_df = df.filter(df.value.contains("pollution")).select(from_json(df.value.cast("string"),pollution_schema).alias("value")).select("value.*").select("kafkatopic","ts")
weather_df = df.filter(df.value.contains("weather")).select(from_json(df.value.cast("string"),weather_schema).alias("value")).select("value.*").select("kafkatopic","ts")

pollution_df.writeStream.outputMode("append").trigger(processingTime="5 seconds").format("console").start()
weather_df.writeStream.outputMode("append").trigger(processingTime="5 seconds").format("console").start().awaitTermination()
