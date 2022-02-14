# Predicting air pollution based on weather <br/> Big Data Analytics course project

This repository contains Big Data Analytics course project implementation. The course was conducted at the Warsaw University of Technology during the 2021/2022 winter semester.

## Project goals description
The goal of the project was to create a system, which will analyze data from two streaming data sources and present it to the user through a web interface. We chose the following data sources:

1. Air pollution from [aqicn.org](https://aqicn.org)
2. Weather from [OpenWeather](https://openweathermap.org)

and set a goal to predict air pollution based on weather.

## System architecture

The system was designed in compliance with the [lambda architecture](https://docs.microsoft.com/en-us/azure/architecture/data-guide/big-data/#lambda-architecture) principles. System architecture overview can be found below:

![architecture-overview](/assets/architecture-overview.png)

### Speed layer
Speed layer contains a single component: Apache Spark. This module is directly connected to Apache Kafka component and utilizes Spark Streaming DataFrames to fetch the data. It runs two jobs:
1. Machine Learning job
2. Real-time on-demand predictions API job

Any output data (model evaluation, model parameters) is sent back to Kafka to be stored in Hadoop. The model which is being trained is an instance of [multilayer perceptron classifier](https://spark.apache.org/docs/latest/ml-classification-regression.html#multilayer-perceptron-classifier)
### Batch layer
Batch layer contains 3 components:
1. Apache Nifi
2. Apache Hadoop
3. Apache Hive

Apache NiFi is responsible for data preprocessing, e.g.:
1. Appending timestamps and ids to JSON data for it to be stored in Hadoop
2. Routing flowfiles to appropriate components 
3. Merging multiple JSON flowfiles into one for Hadoop storing efficiency
4. Converting flowfiles to [ORC](https://cwiki.apache.org/confluence/display/hive/languagemanual+orc) format
5. Feeding data to Hadoop component

Apache Hadoop is used to store all the data ever seen by the system. Once a day, the data is aggregated and sent to MongoDB:
1. Storing all the raw data allows for broad analysis through Apache Hive
2. Aggregated data, which will be presented to the end-user, is recomputed per day and once a day, to not to overload the master dataset

### Serving layer

Serving layer consists of 2 components:
1. React frontend
2. MongoDB database

By connecting to MongoDB database through an auxiliary Docker container, the user interface displays the latest data aggregations. It also displays a real-time view of model evaluation metrics. Frontend preview video can be found [here](https://drive.google.com/file/d/1i4WykbQIrp3vE47AnkCuhxk-DQxDehFP/view).

