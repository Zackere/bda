## Launching

Run `docker-compose up -d` to run the application. After a while, `Apache Nifi` will be available under `htps://localhost:8443/nifi`. For login credentials please refer to `docker-compose.yml`.

## Setting up basic kafka consumer example

Create `ConsumeKafka_2_0` (other conumers are untested/do not work) and `LogAttribute` processors. Connect `ConsumeKafka_2_0` to `LogAttribute`. Disable `LogAttribute`. Set up `ConsumeKafka_2_0` in the following way:

1. `KafkaBrokers=kafka:2181`
2. `Topic name(s)=pollution-delhi`
3. `Group ID=nifi-consumer-1`

Start `ConsumeKafka_2_0`. Soon messages will be available for inspection in the queue.
https://stackoverflow.com/questions/50383997/how-do-i-view-the-consumed-messages-of-kafka-in-nifi

## Stopping the application

Run `docker-compose down`.
