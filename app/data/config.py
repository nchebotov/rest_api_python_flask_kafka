# coding: utf-8

def commit_completed(err, partitions):
    if err:
        print(str(err))
    else:
        print("Committed partition offsets: " + str(partitions))


KAFKA_TOPIC_NAME = "kafka_topic_1"
GROUP = "rest_api_group"
METRICS = "group_metrics"

CONFIG = {
    "bootstrap.servers": "kafka:9092,localhost:29092",
}

CONSUMER_CONF = {
    "group.id": GROUP,
    "auto.offset.reset": "earliest",
    "on_commit": commit_completed,
    "enable.auto.commit": False,
    "enable.partition.eof": True,
    "message.max.bytes": 10485780
}

consumer_metrics_conf = {
    "group.id": METRICS,
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
    "enable.partition.eof": True,
    "message.max.bytes": 10485780
}
