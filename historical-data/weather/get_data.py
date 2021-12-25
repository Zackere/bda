import requests
import json

for countrycode in ['Delhi,in', 'Warsaw,pl', 'Berlin,de', 'Moscow,ru']:
    data = []
    start = 1609545600  # 1st January
    end = 1639785600  # 18th December
    appid = '3cec7b38451aa3ab4da0caacc4fb06e9'
    while end > start:
        print(
            f'Start: {start}, end: {end}, requests left: {(end-start)/(3600 * 169)}')
        res = requests.get(
            f'http://history.openweathermap.org/data/2.5/history/city?q={countrycode}&type=hour&start={start}&end={end}&appid={appid}').json()
        data += res['list']
        start = start + 3600 * 169
    with open(f'{countrycode}.json', 'w') as f:
        f.write(json.dumps(data))
