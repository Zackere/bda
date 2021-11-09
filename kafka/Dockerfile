FROM openjdk:slim
COPY --from=python:3.9 / /

RUN curl https://dlcdn.apache.org/kafka/3.0.0/kafka_2.13-3.0.0.tgz --output kafka_2.13-3.0.0.tgz && \
    tar -xzf kafka_2.13-3.0.0.tgz && \
    python3 -m pip install kafka-python requests

COPY ./kafka/https_consumer.py https_consumer.py
COPY ./kafka/rest_api_producer.py rest_api_producer.py
COPY ./kafka/kafka_startup.sh kafka_startup.sh

CMD ./kafka_startup.sh kafka_2.13-3.0.0
