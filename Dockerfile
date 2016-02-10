FROM python:3.5

RUN apt-get update

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir pytest pytest-cov

COPY . /usr/src/app/

RUN python setup.py develop
