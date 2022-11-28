# coding: utf-8

import json, prometheus_client
from flask import Flask, request, Response
from flask_restful import Api
from flasgger import Swagger, LazyJSONEncoder
from confluent_kafka import Consumer, Producer
from prometheus_client import Counter, CONTENT_TYPE_LATEST, make_wsgi_app, CollectorRegistry
from data.config import *


app = Flask(__name__)
api = Api(app)
app.config.from_pyfile('config-app.cfg')
swag = Swagger(app, template_file='swagger/spec.yml', parse=True)
app.json_encoder = LazyJSONEncoder


#   Rest API microservice metrics
c_request = Counter('rest_api_requests_total', 'HTTP status codes', ['method', 'endpoint'])
c_send_mess = Counter('rest_api_send_message_total', 'Total send message', ['kafka_topic_name', 'partition'])
c_read_mess = Counter('rest_api_read_message_total', 'Total read message', ['kafka_topic_name', 'partition', 'group_id'])
# all_total_mess = Counter('rest_api_all_message_total', 'Total all message', ['kafka_topic_name', 'partition', 'group_id'])


@app.route('/home', methods=['GET'])
def home():
    c_request.labels(method='get', endpoint='/').inc()
    return 'Hello World!', 200


@app.route('/send_data', methods=['POST'])
def send_message():
    c_request.labels(method='post', endpoint='/send_data').inc()
    data = request.data
    p = Producer(config)
    try:
        # Validation of the json format of the incoming POST request from the user
        json.loads(data)
    except ValueError as e:
        print(e)
        return 'Данный формат отправленного сообщения НЕ соответствует формату JSON!'
    else:
        def delivery_report(err, msg):
            if err is not None:
                print('Message delivery failed: {}'.format(err))
            else:
                print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
        # Trigger any available delivery report callbacks from previous produce() calls
        json_str = json.dumps(json.loads(data)).encode('utf-8')
        p.produce(topic=kafka_topic_name, value=json_str, callback=delivery_report)
        c_send_mess.labels(kafka_topic_name=kafka_topic_name, partition=0).inc()
    finally:
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        p.flush()
    return f'''Данный формат отправленного сообщения СООТВЕТСТВУЕТ формату JSON!
              Сообщение успешно записано!''', 200


@app.route('/read_data', methods=['GET'])
def read_messages():
    c_request.labels(method='get', endpoint='/read_data').inc()
    # We extend the base config with a configuration for the consumer
    consumer_conf.update(config)
    cons = Consumer(consumer_conf)
    # Define empty list for kafka consumer messages
    messages = []
    cons.subscribe([kafka_topic_name])
    print("=== Consuming transactional messages from topic {}. ===".format(kafka_topic_name))
    while True:
        msg = cons.poll(timeout=100.0)
        if msg is None:
            print('Message is none!')
            continue
        if msg.error():
            print(f'Kafka error message: {msg.error().code()}')
            break
        if msg:
            payload = msg.value().decode('utf-8')
            print('Received message: {}'.format(json.loads(payload.encode('utf-8'))))
            c_read_mess.labels(group_id=group, kafka_topic_name=kafka_topic_name, partition=0).inc()
            messages.append(json.loads(payload.encode('utf-8')))
            cons.commit(asynchronous=False)
    cons.close()
    if len(messages) > 0:
        return f'{messages[:]}', 200
    else:
        return 'Непрочитанные сообщения отсутствуют!', 204


@app.route('/metrics/')
def metrics():
    return Response(prometheus_client.generate_latest(), content_type='application/json'), 200


@app.errorhandler(500)
def handle_500(error):
    return str(error), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)


