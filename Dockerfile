FROM python:3.11.5-alpine
LABEL maintainer="Esxoyne@GitHub"

ENV PYTHONUNBUFFERED 1

WORKDIR /app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /vol/web/media/
