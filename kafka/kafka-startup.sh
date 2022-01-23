#!/bin/sh

cd $1

./bin/zookeeper-server-start.sh config/zookeeper.properties &
./bin/kafka-server-start.sh     config/server.properties &

create_topic () {
    ./bin/kafka-topics.sh --create   --topic "$1" --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ./bin/kafka-topics.sh --describe --topic "$1" --bootstrap-server localhost:9092
}

for extra_topic in error spark modelweights
do
    create_topic "$extra_topic"
done

for city in delhi warsaw berlin moscow
do
    create_topic "pollution$city"
    create_topic "weather$city"
    create_topic "pollution${city}aggregations"
    create_topic "weather${city}aggregations"
    create_topic "modelpredictions${city}"
done

wait
