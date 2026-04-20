# LLM API Project

FastAPI-проект с JWT-аутентификацией, SQLite и интеграцией с OpenRouter. Приложение позволяет зарегистрировать пользователя, получить токен доступа, отправлять сообщения в LLM, хранить историю переписки и очищать её через API.

## Что умеет

- Регистрация и авторизация пользователя
- Получение профиля текущего пользователя
- Отправка сообщений в LLM через OpenRouter
- Хранение истории чата в SQLite
- Просмотр и удаление истории сообщений

## Стек

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT
- OpenRouter API
- Uvicorn

## Структура API

- `POST /auth/register` - регистрация нового пользователя
- `POST /auth/login` - вход и получение `access_token`
- `GET /auth/me` - профиль текущего пользователя
- `POST /chat` - отправка запроса в модель
- `GET /chat/history` - получение истории переписки
- `DELETE /chat/history` - удаление истории переписки
- `GET /health` - проверка состояния сервиса

## Переменные окружения

Приложение использует `.env` со следующими параметрами:

- `APP_NAME`
- `ENV`
- `JWT_SECRET`
- `JWT_ALG`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `SQLITE_PATH`
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_MODEL`
- `OPENROUTER_SITE_URL`
- `OPENROUTER_APP_NAME`

## Запуск

Установка зависимостей:

```bash
uv sync
```

Запуск сервера:

```bash
uv run uvicorn app.main:app --reload
```

После запуска API будет доступно по адресу:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Как работает сценарий

1. Пользователь регистрируется через `/auth/register`.
2. Затем входит через `/auth/login` и получает Bearer-токен.
3. С этим токеном отправляет запрос на `/chat`.
4. Сообщения сохраняются в базе, а историю можно получить через `/chat/history`.
5. Историю можно полностью очистить через `DELETE /chat/history`.

## Скриншоты

### Registration

![Registration](photos/registration.png)

### Auth

![Auth](photos/auth.png)

### Chat

![Chat](photos/chat.png)

### Hist

![Hist](photos/hist.png)

### Delete

![Delete](photos/delete.png)

### Deleted

![Deleted](photos/deleted.png)
