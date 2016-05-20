FROM python:3.5

RUN apt-get update

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY . /usr/src/app/

RUN pip install --no-cache-dir -e .[dev]
