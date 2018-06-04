FROM python:3.6

RUN mkdir -p /src
RUN pip install --upgrade \
	pycco \
	websocket-client~=0.47.0 \
	pytest~=3.0 \
	bigchaindb-driver==0.5.0a4
RUN pip install --upgrade pip
RUN pip install blns
