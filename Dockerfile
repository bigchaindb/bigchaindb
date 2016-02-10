FROM python:3.5

RUN apt-get update && apt-get -y install vim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir pytest pytest-cov
RUN pip install --no-cache-dir ipython ipdb

COPY . /usr/src/app/

RUN python setup.py develop
