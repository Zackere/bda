#!/bin/bash

startup.sh &

sleep 30 # Wait for db startup
for city in delhi warsaw berlin moscow
do
    sqlcmd="CREATE TABLE pollution$city (id STRING, ts TIMESTAMP, aqi INT, lon FLOAT, lat FLOAT, measured INT) STORED AS ORC LOCATION 'hdfs://namenode:8020/user/nifi/pollution$city';"
    echo "EXECUTING COMMAND \"$sqlcmd\""
    beeline -u jdbc:hive2:// -e "$sqlcmd"
    sqlcmd="CREATE TABLE weather$city (id STRING, ts TIMESTAMP, lon FLOAT, lat FLOAT, temp FLOAT, pressure INT, humidity INT, clouds INT, windspeed FLOAT, winddeg INT, measured INT) STORED AS ORC LOCATION 'hdfs://namenode:8020/user/nifi/weather$city';"
    echo "EXECUTING COMMAND \"$sqlcmd\""
    beeline -u jdbc:hive2:// -e "$sqlcmd"
done

sqlcmd = "CREATE TABLE modelweights (id STRING, ts TIMESTAMP, weights ARRAY<FLOAT>) STORED AS ORC LOCATION 'hdfs://namenode:8020/user/nifi/modelweights';"
echo "EXECUTING COMMAND \"$sqlcmd\""
beeline -u jdbc:hive2:// -e "$sqlcmd"

beeline -u jdbc:hive2:// -e "SHOW TABLES;"

wait
