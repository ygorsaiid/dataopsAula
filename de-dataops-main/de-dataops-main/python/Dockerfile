# NOTE name need to be Dockerfile
FROM python:3.9

WORKDIR /usr/src/python-app

COPY . .
RUN mkdir -p ./data/raw

RUN pip install -r requirements.txt
RUN pip install mysql-connector-python
RUN pip install SQLAlchemy
