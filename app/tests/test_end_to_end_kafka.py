import pytest
import json
from confluent_kafka import Producer, Consumer
from app.tests.data.data_for_tests_app import *


@pytest.mark.parametrize("testdata", [DATA0, DATA1, DATA2, DATA3, DATA5, DATA6, DATA7, DATA8, DATA9, DATA10])
def test_end_to_end_kafka(testdata):
    kafka_topic_name = "kafka_topic_1"
    producer = Producer({"bootstrap.servers": "kafka:9092,localhost:29092"})
    consumer = Consumer({
        "bootstrap.servers": "kafka:9092,localhost:29092",
        "group.id": 'test_group',
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "enable.partition.eof": True,
        "message.max.bytes": 10485780
    })

    json_str = json.dumps(json.loads(testdata)).encode('utf-8')
    producer.produce(topic=kafka_topic_name, value=json_str)
    producer.flush()

    consumer.subscribe([kafka_topic_name])
    messages = []
    while True:
        msg = consumer.poll(100)
        if msg is None:
            break
        if msg.error():
            break
        if msg:
            payload = msg.value()
            if AttributeError:
                pass
            messages.append(json.loads(payload))
    consumer.close()
    assert json.loads(testdata) == json.loads(json.dumps(messages[-1]))

