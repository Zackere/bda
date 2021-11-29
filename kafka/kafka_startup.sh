#!/bin/sh

cd $1

./bin/zookeeper-server-start.sh config/zookeeper.properties &
./bin/kafka-server-start.sh     config/server.properties &

for extra_topic in error spark
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
    python3 /rest_api_producer.py -a "https://api.waqi.info/feed/$city/?token=1d9e5a0caf47598601455f82453f22990f088d82" -t "pollution$city" -s localhost:9092 -d 20 &
done

python3 /rest_api_producer.py -a "https://api.openweathermap.org/data/2.5/weather?q=Delhi,in&appid=2e60ac296b6e007baf4cda66380be86c"  -t weatherdelhi  -s localhost:9092 -d 20 &
python3 /rest_api_producer.py -a "https://api.openweathermap.org/data/2.5/weather?q=Warsaw,pl&appid=2e60ac296b6e007baf4cda66380be86c" -t weatherwarsaw -s localhost:9092 -d 20 &
python3 /rest_api_producer.py -a "https://api.openweathermap.org/data/2.5/weather?q=Berlin,de&appid=2e60ac296b6e007baf4cda66380be86c" -t weatherberlin -s localhost:9092 -d 20 &
python3 /rest_api_producer.py -a "https://api.openweathermap.org/data/2.5/weather?q=Moscow,ru&appid=2e60ac296b6e007baf4cda66380be86c" -t weathermoscow -s localhost:9092 -d 20 &

wait
