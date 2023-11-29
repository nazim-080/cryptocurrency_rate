# Сервис для получения курсов валютных пар с бирж

## Инструкция по развертыванию тестового проекта

### Настройка проекта

Создайте `.env` файл в корне репозитория:

```bash
cp .env.example .env
```

Внесите при необходимости корректировки в переменные окружения.

GECKO_KEY: Это API-ключ для сервиса CoinGecko.

RABBITMQ_DEFAULT_USER и RABBITMQ_DEFAULT_PASS: Это имя пользователя и пароль для доступа к RabbitMQ.

POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST и POSTGRES_PORT: Это параметры для подключения к вашей базе данных Postgres.

PGADMIN_DEFAULT_EMAIL и PGADMIN_DEFAULT_PASSWORD: Это электронная почта и пароль для доступа к интерфейсу PgAdmin. 

### Сборка образов и запуск контейнеров

В корне репозитория выполните команду:

```bash
docker-compose up --build
```

При первом запуске данный процесс может занять несколько минут.

### Остановка контейнеров

Для остановки контейнеров выполните команду:

```bash
docker-compose stop
```
![Снимок экрана от 2023-11-29 04-30-08](https://github.com/nazim-080/cryptocurrency_rate/assets/70864710/10c47e0d-00b2-4303-b133-fddf6466a81b)
