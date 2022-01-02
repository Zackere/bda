
# pip install sasl
# pip install thrift
# pip install thrift-sasl
# pip install PyHive
# pip install pandas
# pip install argparse
# pip install kafka-python

import pandas as pd
from pyhive import hive
import argparse
from datetime import datetime,timedelta
from kafka import KafkaProducer
import json

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument(
    '--date',
    type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
)
args = parser.parse_args()
date = args.date or datetime.now() - timedelta(days=1) # given date or yesterday

start_date = date.strftime('%Y-%m-%d')
end_date = (date + timedelta(days=1)).strftime('%Y-%m-%d')

kafka_producer = KafkaProducer(bootstrap_servers='localhost:9092')
conn = hive.Connection(host="localhost", port=10000, username="hive")

for city in ["berlin","warsaw","delhi","moscow"]:
    pollution = pd.read_sql(f"""
            select min(aqi) as MinAQI, max(aqi) as MaxAQI, avg(aqi) as AvgAQI, '{city}' as City from pollution{city}
            where ts >= '{start_date}' and ts < '{end_date}'
        """, conn)
    print(pollution)
    print(pollution.to_json(orient="records").encode())
    kafka_producer.send('pollutionaggregations',pollution.to_json(orient="records").encode())
    weather = pd.read_sql(f"""
            select 
                min(temp) as MinTemp,           max(temp) as MaxTemp,           avg(temp) as AvgTemp,
                min(pressure) as MinPressure,   max(pressure) as MaxPressure,   avg(pressure) as AvgPressure,
                min(humidity) as MinHumidity,   max(humidity) as MaxHumidity,   avg(humidity) as AvgHumidity,
                min(clouds) as MinClouds,       max(clouds) as MaxClouds,       avg(clouds) as AvgClouds,
                min(windspeed) as MinWindspeed, max(windspeed) as MaxWindspeed, avg(windspeed) as AvgWindspeed,
                min(winddeg) as MinWindDegree,  max(winddeg) as MaxWindDegree,  avg(winddeg) as AvgWindDegree,
                '{city}' as City
            from weather{city}
            where ts between '{start_date}' and '{end_date}'
        """, conn)
    print(weather)
    print(weather.to_json(orient="records").encode())
    kafka_producer.send('weatheraggregations',weather.to_json(orient="records").encode())
