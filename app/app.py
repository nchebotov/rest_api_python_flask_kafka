# encoding: utf-8

import json
import prometheus_client
from flask import Flask, request, Response
from flask_restful import Api
from flasgger import Swagger, LazyJSONEncoder
from confluent_kafka import Consumer, Producer
from prometheus_client import Counter, Gauge, CollectorRegistry


app = Flask(__name__)
api = Api(app)
app.config.from_pyfile('config-app.cfg')
swag = Swagger(app, template_file='swagger/spec.yml', parse=True)
app.json_encoder = LazyJSONEncoder


#   Rest API microservice metrics
registry = CollectorRegistry()

c_request = Counter('rest_api_requests_total', 'HTTP status codes', ['method', 'endpoint'], registry=registry)

c_send_mess = Counter('rest_api_send_message_total', 'Total send message',
                      ['kafka_topic_name', 'partition'], registry=registry)

c_read_mess = Counter('rest_api_read_message_total', 'Total read message',
                      ['group_id', 'kafka_topic_name', 'partition'], registry=registry)

all_total_mess = Gauge('rest_api_all_message_topic_total', 'Total all message in topic Kafka',
                       ['group_id', 'kafka_topic_name', 'partition'], registry=registry)


def all_mess():
    app.config['CONSUMER_METRICS_CONF'].update(app.config['CONFIG'])
    cons = Consumer(app.config['CONSUMER_METRICS_CONF'])
    cons.subscribe([app.config['KAFKA_TOPIC_NAME']])
    count = 0
    while True:
        msg = cons.poll(timeout=5.0)
        if msg is None:
            continue
        if msg.error():
            break
        if msg:
            count += 1
            all_total_mess.labels(group_id=app.config['METRICS'], kafka_topic_name=app.config['KAFKA_TOPIC_NAME'], partition=0).set(count)
    cons.close()


@app.route('/home', methods=['GET'])
def home():
    c_request.labels(method='get', endpoint='/').inc()
    return 'Hello World!', 200


@app.route('/send_data', methods=['POST'])
def send_message():
    c_request.labels(method='post', endpoint='/send_data').inc()
    data = request.data
    p = Producer(app.config['CONFIG'])
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
        p.produce(topic=app.config['KAFKA_TOPIC_NAME'], value=json_str, callback=delivery_report)
        c_send_mess.labels(kafka_topic_name=app.config['KAFKA_TOPIC_NAME'], partition=0).inc()
    finally:
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        p.flush()
    return f'Данный формат отправленного сообщения СООТВЕТСТВУЕТ формату JSON! Сообщение успешно записано!', 200


@app.route('/read_data', methods=['GET'])
def read_messages():
    c_request.labels(method='get', endpoint='/read_data').inc()
    # We extend the base config with a configuration for the consumer
    app.config['CONSUMER_CONF'].update(app.config['CONFIG'])
    cons = Consumer(app.config['CONSUMER_CONF'])
    # Define empty list for kafka consumer messages
    messages = []
    cons.subscribe([app.config['KAFKA_TOPIC_NAME']])
    print("=== Consuming transactional messages from topic {}. ===".format(app.config['KAFKA_TOPIC_NAME']))
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
            c_read_mess.labels(group_id=app.config['GROUP'], kafka_topic_name=app.config['KAFKA_TOPIC_NAME'], partition=0).inc()
            messages.append(json.loads(payload.encode('utf-8')))
            cons.commit(asynchronous=False)
    cons.close()
    if len(messages) > 0:
        return f'{messages[:]}', 200
    else:
        return 'Непрочитанные сообщения отсутствуют! Status code: 204'


@app.route('/metrics/')
def metrics():
    all_mess()
    return Response(prometheus_client.generate_latest(registry), mimetype='text/plain'), 200


@app.errorhandler(500)
def handle_500(error):
    return str(error), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
