FROM python:3.6-alpine

COPY ./requirements.txt /

RUN apk --no-cache add build-base bash postgresql-dev \
    && pip install -r requirements.txt \
    && apk del build-base

COPY . /app

WORKDIR /app

EXPOSE 5000

CMD ./manage.py runserver -h 0.0.0.0