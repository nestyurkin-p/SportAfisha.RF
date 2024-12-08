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

### Валидация учетных данных

Принимает сообщения из очереди `oauth-validate-request-queue` на проверку аутентификационных данных в следующем формате:

``` json
{
    "token": "<bearer token>"
}
```

И пушит в `oauth-validate-response-queue` следующее:

``` json
{
    "token": "<bearer token>",
    "validated": true | false,
    < "role": "<one of: athlete | office | superuser>" >
}
```

`"role"` включено в ответ при условии, что `"validated" == true`.

### Регистрация

Принимает сообщения из очереди `oauth-register-request-queue` на регистрацию сущности в следующем формате:

``` json
{
    "email": "<email>",
    "require_email_verification": true | false,
    "password": "<password>",
}
```

И пушит в `oauth-register-response-queue` следующее следом:

``` json
{
    "email": "<email>",
    "status": "<one of: email_pending | email_verified | user_already_exists>"
}
```

Если `"require_email_verification" == true`, то `"status" = "email_pending"`, при этом OAuth2 отправляет следующее сообщение в `email-request-queue`:

``` json
{
    "address": "<email address>",
    "content": "Ссылка для подтверждения: http://oauth2/verify?token=<verification token>"
}

```
