import pandas as pd
from pyhive import hive
import argparse
from datetime import datetime, timedelta
from kafka import KafkaProducer
import json

parser = argparse.ArgumentParser()
parser.add_argument(
    '--date',
    type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
)
args = parser.parse_args()
date = args.date or datetime.now() - timedelta(days=1)  # given date or yesterday

start_date = (date - datetime(1970, 1, 1)).total_seconds()
end_date = (date + timedelta(days=1) - datetime(1970, 1, 1)).total_seconds()

kafka_producer = KafkaProducer(bootstrap_servers='kafka:9092')
conn = hive.Connection(host='hive-server')

for city in ['berlin', 'warsaw', 'delhi', 'moscow']:
    pollution = pd.read_sql(f"""
            select min(aqi) as MinAQI, max(aqi) as MaxAQI, avg(aqi) as AvgAQI, '{city}' as City, '{start_date}' as `Date` from pollution{city}
            where measured between {start_date} and {end_date}
        """, conn)
    if not pollution.isnull().values.any():
        kafka_producer.send('pollutionaggregations', json.dumps(
            pollution.to_dict('records')[0]).encode())
    weather = pd.read_sql(f"""
            select 
                min(temp) as MinTemp,           max(temp) as MaxTemp,           avg(temp) as AvgTemp,
                min(pressure) as MinPressure,   max(pressure) as MaxPressure,   avg(pressure) as AvgPressure,
                min(humidity) as MinHumidity,   max(humidity) as MaxHumidity,   avg(humidity) as AvgHumidity,
                min(clouds) as MinClouds,       max(clouds) as MaxClouds,       avg(clouds) as AvgClouds,
                min(windspeed) as MinWindspeed, max(windspeed) as MaxWindspeed, avg(windspeed) as AvgWindspeed,
                min(winddeg) as MinWindDegree,  max(winddeg) as MaxWindDegree,  avg(winddeg) as AvgWindDegree,
                '{city}' as City, {start_date} as `Date`
            from weather{city}
            where measured between {start_date} and {end_date}
        """, conn)
    if not weather.isnull().values.any():
        kafka_producer.send('weatheraggregations', json.dumps(
            weather.to_dict('records')[0]).encode())
