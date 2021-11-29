import requests
from argparse import ArgumentParser
from time import sleep
from kafka import KafkaProducer

ERROR_TOPIC = 'error'


def build_argparser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-a')
    parser.add_argument('-t')
    parser.add_argument('-s')
    parser.add_argument('-d', type=int, choices=range(1, 999))
    return parser


def main(remote_address, topic, bootstrap_servers, sleep_duration):
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers)
    while True:
        sleep(sleep_duration)
        try:
            response = requests.get(remote_address)
            producer.send(topic, value=response.content).get()
        except Exception as e:
            producer.send(ERROR_TOPIC, value=str(e)).get()
        producer.flush()


if __name__ == '__main__':
    args = build_argparser().parse_args()
    main(args.a, args.t, args.s, args.d)
