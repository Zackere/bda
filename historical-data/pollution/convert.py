import pandas as pd
from glob import glob
from datetime import date
from os import path
import json
import random

coordinates = {
    'delhi.json':  {'lon': 28.63576,  'lat': 77.22445},
    'warsaw.json': {'lon': 52.22517,  'lat': 21.014784},
    'berlin.json': {'lon': 52.520008, 'lat': 13.404954},
    'moscow.json': {'lon': 55.759354, 'lat': 37.595585},
}


def convert(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    if 'pm25' not in df:
        df['pm25'] = df['pm10']
    elif 'pm10' in df:
        df['pm25'].fillna(3 * df['pm10'], inplace=True)
    df = df[['date', 'pm25']]
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] > pd.to_datetime(date(2021, 1, 1))]
    df['date'] = (df['date'] - pd.Timestamp('1970-01-01')
                  ) // pd.Timedelta('1s')
    df = df[['date', 'pm25']]
    df.set_axis(['measured', 'aqi'], axis=1, inplace=True)
    df['aqi'] = df['aqi'].astype(int)
    df['lon'] = [coordinates[target_filename]['lon']] * len(df)
    df['lat'] = [coordinates[target_filename]['lat']] * len(df)
    df.sort_values('measured', inplace=True, ascending=True)
    return df.to_dict(orient='records')


def interpolate_to_hourly_data(data):
    for a, b in zip(data, data[1:]):
        yield a
        start = a['measured'] + 3600
        end = b['measured']
        while start < end:
            random.seed(start)
            aqi = a['aqi'] + (b['aqi'] - a['aqi']) * (start -
                                                      a['measured']) / (b['measured'] - a['measured'])
            err = random.uniform(-aqi/4, aqi/4)  # 25% error
            yield {
                'lon': a['lon'],
                'lat': a['lat'],
                'measured': start,
                'aqi': int(aqi + err)
            }
            start += 3600
    yield data[-1]


for p in glob('raw/*.csv'):
    target_filename = path.basename(p).replace('.csv', '.json')
    data = list(interpolate_to_hourly_data(convert(p)))
    with open(target_filename, 'w', newline='\n') as f:
        f.write(json.dumps(data, indent=2, sort_keys=True))
