FROM --platform=linux/amd64 python:3.10

RUN apt-get update

RUN apt-get -y install git && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install https://github.com/tanishq-acu/MetaGPT/archive/main.zip

COPY . .