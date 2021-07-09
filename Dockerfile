FROM python:3.7.1-slim

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . ./

CMD uvicorn --host=0.0.0.0 app.main:app
