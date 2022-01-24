from datetime import datetime
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.ml.feature import VectorAssembler
import os
from pyhive import hive
import base64
import shutil
import os
from pyspark.ml.classification import MultilayerPerceptronClassificationModel, MultilayerPerceptronClassifier
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


@app.route('/predict', methods=['POST'])
def predict():
    spark = SparkSession.builder.appName('BDAModel').getOrCreate()
    spark.sparkContext.setLogLevel('WARN')
    logger = spark.sparkContext._jvm.org.apache.log4j.LogManager.getLogger(
        __name__)
    logger.warn('Recieved request')
    logger.warn(request.json)
    posted_data = spark.sparkContext.parallelize([request.json])
    model = None

    try:
        logger.warn('Connecting to hive')
        conn = hive.Connection(host='hive-server')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM modelweights ORDER BY ts DESC')
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
        raise ex

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

    raise Exception('No model available')


@app.route('/hotmodelaggregations')
def hotmodelaggregations():
    city = request.args.get('city')
    if city not in ['delhi', 'berlin', 'warsaw', 'moscow']:
        raise Exception()
    spark = SparkSession.builder.appName('BDAModel').getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel('WARN')
    logger = sc._jvm.org.apache.log4j.LogManager.getLogger(__name__)
    logger.warn(f'Recieved request for city: {city}')

    logger.warn('Connecting to hive')
    conn = hive.Connection(host='hive-server')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM modelpredictions{city} ORDER BY ts ASC')
    rdd = spark.sparkContext.parallelize(cursor.fetchall())
    daily_avg_acc = rdd.map(lambda x: (x[1].timestamp() // (3600 * 24), (x[2] == x[3], 1))).reduceByKey(
        lambda a, b: (a[0]+b[0], a[1]+b[1])).map(lambda x: (x[0], x[1][0]/x[1][1])).sortByKey()
    daily_avg_dist = rdd.map(lambda x: (x[1].timestamp() // (3600 * 24), (abs(x[2] - x[3]), 1))).reduceByKey(
        lambda a, b: (a[0]+b[0], a[1]+b[1])).map(lambda x: (x[0], x[1][0]/x[1][1])).sortByKey()
    avg_acc = rdd.map(lambda x: x[2] == x[3]).mean()
    avg_dist = rdd.map(lambda x: abs(x[2] - x[3])).mean()
    cursor.close()
    conn.close()
    return jsonify({
        'dailyAvgAcc': [{'acc': x[1], 'date': datetime.utcfromtimestamp(int(x[0] * 3600 * 24))} for x in daily_avg_acc.collect()],
        'dailyAvgDist': [{'dist': x[1], 'date': datetime.utcfromtimestamp(int(x[0] * 3600 * 24))} for x in daily_avg_dist.collect()],
        'avgAcc': avg_acc,
        'avgDist': avg_dist,
    })


app.run('0.0.0.0', 4444, debug=True)
