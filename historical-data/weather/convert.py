import json
from glob import glob
from os import path

coordinates = {
    'delhi.json':  {'lon': 28.63576,  'lat': 77.22445},
    'warsaw.json': {'lon': 52.22517,  'lat': 21.014784},
    'berlin.json': {'lon': 52.520008, 'lat': 13.404954},
    'moscow.json': {'lon': 55.759354, 'lat': 37.595585},
}

for data in glob('raw/*.json'):
    target_filename = f'{path.basename(data.split(",")[0].lower())}.json'
    with open(data) as f:
        data = json.loads(f.read())
    data = sorted(data, key=lambda j: j['dt'])
    data = [
        {
            'measured': d['dt'],
            'temp': float(d['main']['temp']),
            'pressure': d['main']['pressure'],
            'humidity': d['main']['humidity'],
            'windspeed': float(d['wind']['speed']),
            'winddeg': d['wind']['deg'],
            'clouds': d['clouds']['all'],
            **coordinates[target_filename],
        }
        for d in data
    ]
    with open(target_filename, 'w', newline='\n') as f:
        f.write(json.dumps(data, indent=2, sort_keys=True))
