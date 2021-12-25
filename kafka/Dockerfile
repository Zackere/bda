FROM openjdk:slim

RUN apt-get update -y && apt-get install curl -y && \
    curl https://dlcdn.apache.org/kafka/3.0.0/kafka_2.13-3.0.0.tgz --output kafka_2.13-3.0.0.tgz && \
    tar -xzf kafka_2.13-3.0.0.tgz

COPY ./kafka-startup.sh .

CMD ./kafka-startup.sh kafka_2.13-3.0.0
