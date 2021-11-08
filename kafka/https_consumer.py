from kafka import KafkaConsumer
import requests
from argparse import ArgumentParser
import json


def build_arsparser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-t')
    parser.add_argument('-s')
    parser.add_argument('-d')
    return parser


def main(topics, servers, destination):
    payloads = {topic: None for topic in topics}
    for msg in KafkaConsumer(*topics, bootstrap_servers=servers):
        payloads[msg.topic] = msg.value.decode('utf-8')
        if any(map(lambda topic: payloads[topic] is None, topics)):
            continue
        try:
            requests.post(destination, data=json.dumps(payloads))
            payloads = {topic: None for topic in topics}
        except Exception as e:
            print(e.args)


if __name__ == '__main__':
    args = build_arsparser().parse_args()
    main(args.t.split(','), args.s, args.d)
