FROM bitnami/spark:3

USER root
RUN apt-get update -y && \
    apt-get install -y g++ libsasl2-modules libsasl2-dev && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install numpy kafka-python sasl thrift thrift-sasl PyHive flask flask-cors
ENV SASL_PATH=/usr/lib/x86_64-linux-gnu/sasl2
RUN mkdir /models
RUN chown 1001:1001 /models
RUN chown 1001:1001 .
USER 1001

COPY model.py .
COPY server.py .
EXPOSE 4444


CMD /opt/bitnami/scripts/spark/run.sh & \
    spark-submit \
        --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 \
        --conf spark.jars.ivy=/tmp/.ivy \
        model.py & \
    spark-submit \
        --conf spark.jars.ivy=/tmp/.ivy \
        server.py & \
    wait
