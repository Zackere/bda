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
    for msgs in zip(*map(lambda t: KafkaConsumer(t, bootstrap_servers=servers), topics)):
        try:
            requests.post(destination, data=json.dumps({
                          m.topic: json.loads(m.value) for m in msgs}))
        except Exception as e:
            print(e.args)


if __name__ == '__main__':
    args = build_arsparser().parse_args()
    main(args.t.split(','), args.s, args.d)
