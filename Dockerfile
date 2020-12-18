FROM ubuntu:20.04

MAINTAINER Vladislav I. Kulbatski

WORKDIR /usr/src/app

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends\
 python3=3.8.2-0ubuntu2 python-pip-whl=20.0.2-5ubuntu1 python3-pip=20.0.2-5ubuntu1\
 mongo-tools=3.6.3-0ubuntu1\
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install -r requirments.txt

CMD [ "python3", "./main.py" ]