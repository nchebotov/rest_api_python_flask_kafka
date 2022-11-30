# coding: utf-8

def commit_completed(err, partitions):
    if err:
        print(str(err))
    else:
        print("Committed partition offsets: " + str(partitions))


kafka_topic_name = "kafka_topic_1"
group = "rest_api_group"
metric = "group_metrics"

config = {
    "bootstrap.servers": "kafka:9092,localhost:29092",
}

consumer_conf = {
    "group.id": group,
    "auto.offset.reset": "earliest",
    "on_commit": commit_completed,
    "enable.auto.commit": False,
    "enable.partition.eof": True,
    "message.max.bytes": 10485780
}

consumer_metrics_conf = {
    "group.id": metric,
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
    "enable.partition.eof": True,
    "message.max.bytes": 10485780
}
