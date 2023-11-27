FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get -y update \
   && apt-get -y install netcat-openbsd


RUN pip install poetry
COPY pyproject.toml .
COPY poetry.lock .
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .
RUN chmod +x wait-for-rabbitmq.sh
