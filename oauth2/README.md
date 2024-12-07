# Сервис аутентификации

Аутентификация происходит через протокол OAuth2. Подробнее см. C4 диаграмму проекта.

## Настройка окружения и запуск

1. Сгенерировать HS256 JWT ключ для подписи токенов аутентификации:

``` sh
mkdir .secrets
openssl rand -hex 32 > .secrets/jwt_secret_key
```

3. Придумать и записать пароль от главного пользователя PostgreSQL в файл `.secrets/postgres_root_password`

5. Придумать и записать пароль от Redis в двойных кавычках в переменную в файле `.env`:

``` sh
# В .env файле:
REDIS_PASSWORD="пароль"
```

## Запуск

``` sh
docker compose up --build
```

## Коммуникация между микросервисами

Происходит посредством очередй сообщений `RabbitMQ`. Всё взаимодействие с сервисом происходит через `oauth-queue`.

### Валидация учетных данных

Принимает сообщения из очереди на проверку аутентификационных данных в следующем формате:

``` json
{
    "sender": "<sender service name>",
    "type": "validate",
    "token": "<bearer token>"
}
```

И пушит следующее следом:

``` json
{
    "sender": "oauth2",
    "type": "validate",
    "token": "<bearer token>",
    "role": "<one of: athlete | office | superuser>"
    "validated": true | false
}
```

### Регистрация

Запрос на регистрацию сущности:

``` json
{
    "sender": "<sender service name>",
    "type": "register",
    "email": "<email>",
    "require_email_verification": true | false,
    "password": "<password>",
}
```

Ответ:

``` json
{
    "sender": "oauth2",
    "type": "register",
    "email": "<email>",
    "email_status": "<one of: pending_verification | verified>"
}
```
