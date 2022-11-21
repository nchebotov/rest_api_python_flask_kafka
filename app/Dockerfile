# syntax=docker/dockerfile:1
FROM python:3.10-alpine
MAINTAINER Chebotov Nikita 'nikitacebotov0@gmail.com'

RUN apk add --update --no-cache alpine-sdk bash python3
WORKDIR /root

RUN git clone https://github.com/edenhill/librdkafka.git
WORKDIR /root/librdkafka
RUN /root/librdkafka/configure
RUN make
RUN make install

WORKDIR ../app
COPY . .

RUN apk add --no-cache gcc make librdkafka-dev python3 python3-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python"]
CMD ["app.py"]
