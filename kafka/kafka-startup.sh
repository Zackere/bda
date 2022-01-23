#!/bin/sh

cd $1

./bin/zookeeper-server-start.sh config/zookeeper.properties &
./bin/kafka-server-start.sh     config/server.properties &

for extra_topic in error spark modelweights modelpredictions
do
    ./bin/kafka-topics.sh --create   --topic "$extra_topic" --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ./bin/kafka-topics.sh --describe --topic "$extra_topic" --bootstrap-server localhost:9092
done

for city in delhi warsaw berlin moscow
do
    ./bin/kafka-topics.sh --create   --topic "pollution$city" --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ./bin/kafka-topics.sh --describe --topic "pollution$city" --bootstrap-server localhost:9092
    ./bin/kafka-topics.sh --create   --topic "weather$city"   --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ./bin/kafka-topics.sh --describe --topic "weather$city"   --bootstrap-server localhost:9092
    
    ./bin/kafka-topics.sh --create   --topic "pollution${city}aggregations" --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ./bin/kafka-topics.sh --describe --topic "pollution${city}aggregations" --bootstrap-server localhost:9092
    ./bin/kafka-topics.sh --create   --topic "weather${city}aggregations"   --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ./bin/kafka-topics.sh --describe --topic "weather${city}aggregations"   --bootstrap-server localhost:9092
    
done

wait
