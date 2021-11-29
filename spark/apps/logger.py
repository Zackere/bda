from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("LoggerApp").getOrCreate()
spark.sparkContext.setLogLevel("WARN")
df = spark.readStream.format("kafka").option("kafka.bootstrap.servers","kafka:9092").option("subscribe","spark").load()
df.selectExpr("CAST(value AS STRING)").writeStream.outputMode("append").trigger(processingTime="5 seconds").format("console").start().awaitTermination()
