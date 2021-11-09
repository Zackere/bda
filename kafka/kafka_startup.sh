#!/bin/sh

cd $1

./bin/zookeeper-server-start.sh config/zookeeper.properties &
./bin/kafka-server-start.sh     config/server.properties &

for topic in weather-delhi pollution-delhi
do
    ./bin/kafka-topics.sh --create   --topic $topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ./bin/kafka-topics.sh --describe --topic $topic --bootstrap-server localhost:9092
done

python3 /rest_api_producer.py -a "https://api.waqi.info/feed/delhi/?token=1d9e5a0caf47598601455f82453f22990f088d82"                  -t pollution-delhi -s localhost:9092 -d 2 & 
python3 /rest_api_producer.py -a "https://api.openweathermap.org/data/2.5/weather?q=Delhi,in&appid=2e60ac296b6e007baf4cda66380be86c" -t weather-delhi   -s localhost:9092 -d 2 & 

wait
