FROM python:3.11-slim

RUN apt-get update
RUN apt-get install wget -y

COPY src src
COPY data data
COPY requirements/requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /src

ENTRYPOINT uvicorn api:app --host 0.0.0.0 --port 8000