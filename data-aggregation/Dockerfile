FROM python:3.9

RUN apt-get update -y && \
    apt-get install -y g++ libsasl2-modules libsasl2-dev cron && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install numpy pandas kafka-python sasl thrift thrift-sasl PyHive
ENV SASL_PATH=/usr/lib/x86_64-linux-gnu/sasl2
COPY aggregate.py /
COPY aggregate_cron /etc/cron.d/
RUN chmod 0644 /etc/cron.d/aggregate_cron && \
    crontab /etc/cron.d/aggregate_cron

CMD cron -f