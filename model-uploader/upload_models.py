from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import shutil
import base64
from kafka import KafkaProducer
import json
import os
import time

for i in range(100):
    print(f'Connecting to kafka for {i}th time...')
    try:
        kafka_producer = KafkaProducer(bootstrap_servers='kafka:9092')
        break
    except Exception as ex:
        print(ex)
        time.sleep(5)


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_created(event):
        print(f'Noticed creation of: {event}')
        if not event.is_directory:
            return
        time.sleep(1)
        print(f'Now handling: {event}', flush=True)
        shutil.make_archive('/model', 'gztar', event.src_path)
        with open('/model.tar.gz', 'rb') as f:
            data = f.read()
        data = base64.b64encode(data).decode('ascii')
        kafka_producer.send('modelweights', json.dumps({
            'weights': data
        }).encode())
        shutil.rmtree(event.src_path)
        os.remove('/model.tar.gz')


observer = Observer()
observer.schedule(Handler(), '/models')
observer.start()

while True:
    time.sleep(1)
