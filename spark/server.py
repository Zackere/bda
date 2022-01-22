from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.ml.feature import VectorAssembler
import os
from pyhive import hive
import base64
import shutil
import os
from pyspark.ml.classification import MultilayerPerceptronClassificationModel, MultilayerPerceptronClassifier
from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def hello_world():
  return "Hello, World!"

@app.route('/predict', methods=['POST'])
def predict():
    spark = SparkSession.builder.appName('BDAModel').getOrCreate()
    spark.sparkContext.setLogLevel('WARN')
    logger = spark.sparkContext._jvm.org.apache.log4j.LogManager.getLogger(
        __name__)
    logger.warn('Recieved request')
    logger.warn(request.json)
    posted_data = spark.sparkContext.parallelize([request.json])

    try:
        logger.warn('Connecting to hive')
        conn = hive.Connection(host='hive-server')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM modelweights ORDER BY ts DESC')
        row = cursor.fetchone()
        if row:
            # Index dependent on table schema
            logger.warn('Loading model')
            weights_data = row[-1]
            archive_path = './db_model_weights.tar.gz'
            folder_path = './db_model_weights'
            with open(archive_path, 'wb+') as f:
                f.write(base64.b64decode(weights_data))
            shutil.unpack_archive(archive_path, folder_path)
            model = MultilayerPerceptronClassificationModel.load(folder_path)
            shutil.rmtree(folder_path)
            os.remove(archive_path)
        cursor.close()
        conn.close()
    except Exception as ex:
        logger.error(f'{ex}')
        logger.warn('Loading model failed')
        return str('Failed')

    if model != None:
        logger.warn(f'Model weights {model.weights}')
        df = spark.read.json(posted_data)
        df.show(truncate=False)
        asm = VectorAssembler(inputCols=df.columns, outputCol='features')
        df_with_features = asm.transform(df)
        result = model.transform(df_with_features)
        predictions = result.select("prediction", "probability")
        predictions.show(truncate=True)
        return str(predictions.toJSON().first())

    return str('Failed')

app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 4444)),debug=True)