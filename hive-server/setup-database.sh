#!/bin/bash

startup.sh &

sleep 30 # Wait for db startup
sqlcmd=""
for city in delhi warsaw berlin moscow
do
    sqlcmd="${sqlcmd}CREATE TABLE pollution$city (id STRING, ts TIMESTAMP, aqi INT, lon FLOAT, lat FLOAT, measured INT) STORED AS ORC LOCATION 'hdfs://namenode:8020/user/nifi/pollution$city';"
    sqlcmd="${sqlcmd}CREATE TABLE weather$city (id STRING, ts TIMESTAMP, lon FLOAT, lat FLOAT, temp FLOAT, pressure INT, humidity INT, clouds INT, windspeed FLOAT, winddeg INT, measured INT) STORED AS ORC LOCATION 'hdfs://namenode:8020/user/nifi/weather$city';"
    sqlcmd="${sqlcmd}CREATE TABLE modelpredictions$city (id STRING, ts TIMESTAMP, prediction INT, actual INT, weatherid STRING, pollutionid STRING, city STRING) STORED AS ORC LOCATION 'hdfs://namenode:8020/user/nifi/modelpredictions$city';"
done

sqlcmd="${sqlcmd}CREATE TABLE modelweights (id STRING, ts TIMESTAMP, weights STRING) STORED AS ORC LOCATION 'hdfs://namenode:8020/user/nifi/modelweights';"
echo "EXECUTING COMMAND \"$sqlcmd\""
beeline -u jdbc:hive2:// -e "$sqlcmd"

beeline -u jdbc:hive2:// -e "SHOW TABLES;"

wait
