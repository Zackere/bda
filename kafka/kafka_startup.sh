#!/bin/sh

cd $1

./bin/zookeeper-server-start.sh config/zookeeper.properties &
./bin/kafka-server-start.sh config/server.properties &

for topic in weather pollution
do
    ./bin/kafka-topics.sh --create   --topic $topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ./bin/kafka-topics.sh --describe --topic $topic --bootstrap-server localhost:9092
done

# TODO(replinw): Replace kafka-console-producer.sh with rest_api_producer.py
( while :; do echo "{\"weather\":321}"  | ./bin/kafka-console-producer.sh --topic weather    --bootstrap-server localhost:9092; sleep 2; done ) &
( while :; do echo "{\"pollution\":123}" | ./bin/kafka-console-producer.sh --topic pollution --bootstrap-server localhost:9092; sleep 1; done ) &

exec python3 /https_consumer.py -t weather,pollution -s localhost:9092 -d http://host.docker.internal:20200
