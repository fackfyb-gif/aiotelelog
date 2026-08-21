<p align="right">
  <a href="README.md">English README</a> 
    <br>
  <a href="README.fa.md">نسخه فارسی README</a>
</p>

<p align="center">
  <img src="assets/logo.svg" alt="aiotelelog" width="640">
</p>

<h1 align="center">aiotelelog</h1>

<p align="center">
  Типизированный асинхронный Python-клиент для Telegram API funstat.
</p>

`aiotelelog` — асинхронная, типизированная библиотека на Python с моделями
Pydantic для API `funstat`. Она поддерживает все 20 endpoint-ов из
`swagger.json`, пагинацию, стоимость запросов и ошибки API.

## Возможности

- Python 3.10+
- `httpx.AsyncClient` и полная поддержка `async with`
- модели Pydantic v2 для схем Swagger
- полные type hints для публичных методов
- Bearer JWT-аутентификация
- массивы query-параметров, например `id=1&id=2`
- типизированная пагинация и async-итераторы
- отдельные исключения для сетевых и HTTP-ошибок
- токены не записываются в логи

## Установка

Из PyPI:

```bash
python -m pip install funstat-client
```

Из исходников:

```bash
git clone https://github.com/loopy-iri/aiotelelog.git
cd aiotelelog
python -m pip install -e .
```

## Получение API-токена

Swagger не описывает протокол выдачи токенов. Точкой входа сервиса является
маршрут `/api`.

1. Откройте страницу `/api`, например `https://YOUR_API_HOST/api`.
2. Выполните инструкции регистрации или выдачи токена, показанные сервисом.
3. Если требуется подтверждение Telegram, напишите
   [`@funwordsffbot`](https://t.me/funwordsffbot) и выполните команды, которые
   покажет бот.
4. Храните токен только в secret manager или переменной окружения:

```bash
export FUNSTAT_BASE_URL="https://YOUR_API_HOST"
export FUNSTAT_TOKEN="paste-token-here"
```

Библиотека предоставляет type-safe ссылки для этого процесса:

```python
from funstat import token_guide

guide = token_guide("https://YOUR_API_HOST")
print(guide.api_url)       # https://YOUR_API_HOST/api
print(guide.telegram_url)  # https://t.me/funwordsffbot
print(guide.instructions())
```

SDK намеренно не отправляет выдуманный запрос выдачи токена, потому что такой
контракт отсутствует в `swagger.json`.

## Быстрый старт

```python
import asyncio
import os

from funstat import FunstatClient


async def main() -> None:
    async with FunstatClient(
        os.environ["FUNSTAT_BASE_URL"],
        os.environ["FUNSTAT_TOKEN"],
    ) as api:
        result = await api.users.stats_min(123456789)
        if result.data is not None:
            print(result.data.first_name)
            print(result.data.total_msg_count)
            print(f"стоимость запроса: {result.tech.request_cost}")


asyncio.run(main())
```

## Пагинация

Ручное управление страницами:

```python
page = await api.users.messages(123456789, page=1, page_size=50)
for message in page.data or []:
    print(message.message_id, message.text)
```

Или асинхронный перебор всех страниц:

```python
async for message in api.users.iter_messages(123456789, page_size=100):
    print(message.message_id)

async for match in api.text.iter_search("python", page_size=50):
    print(match.user_id, match.group)
```

Для платных endpoint-ов используйте итераторы только тогда, когда нужны все
страницы, поскольку это может создать много запросов.

## Ресурсы SDK

```python
api.groups.common_groups(ids)
api.groups.get(group_id)
api.groups.members(group_id)

api.users.gifts_relation(user_id, page, page_size)
api.users.stickers(user_id)
api.users.common_groups_stat(user_id)
api.users.reputation(user_id)
api.users.name_usage(name, page, page_size)
api.users.username_usage(username)
api.users.resolve_username(names)
api.users.stats_min(user_id)
api.users.stats(user_id)
api.users.basic_info_by_id(ids)
api.users.groups_count(user_id, only_msg=True)
api.users.messages(user_id, page, page_size, ...)
api.users.messages_count(user_id)
api.users.groups(user_id)
api.users.names(user_id)
api.users.usernames(user_id)

api.text.search(input, page, page_size)
```

## Ответы и модели

Большинство endpoint-ов возвращают общий envelope:

```python
ApiResponse[T](
    success=True,
    tech=TechInfo(...),
    data=T | None,
    paging=Paging | None,
)
```

Публичные модели можно импортировать напрямую:

```python
from funstat import ApiResponse, UserMsg, UserStats

payload: ApiResponse[UserStats]
```

Pydantic преобразует имена API в Python-имена: например, `pageSize` доступно как
`page_size`, а `current_ballance` — как `current_balance`.

## Обработка ошибок

```python
from funstat import FunstatError, ProblemError

try:
    result = await api.users.stats(123)
except ProblemError as exc:
    print(exc.status)
    print(exc.problem)
except FunstatError as exc:
    print(f"ошибка запроса: {exc}")
```

`ProblemError` используется для HTTP-ошибок `401`, `403`, `500` и других
неуспешных статусов. Распарсенная модель `AppProblem` находится в
`exc.problem`.

## Разработка и тестирование

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m build
```

Тесты используют `httpx.MockTransport`, поэтому настоящий токен и сеть не
нужны.

## Документация

- [Документация API на английском](docs/API.en.md)
- [مستندات کامل فارسی](docs/API.fa.md)
- [Complete English API documentation](docs/API.en.md)
- [Русский README](README.ru.md)
- [План разработки библиотеки](docs/PYTHON_LIBRARY_PLAN.md)

## Git и релизы

Первоначальная настройка:

```bash
git remote add origin https://github.com/loopy-iri/aiotelelog.git
git branch -M main
git add .
git commit -m "feat: add typed async funstat client"
git push -u origin main
```

Создание release tag:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

С GitHub CLI:

```bash
gh auth login
gh release create v0.1.0 --title "v0.1.0" --generate-notes
```

Для следующей версии обновите `pyproject.toml` и `CHANGELOG.md`:

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main --follow-tags
```

## Лицензия

Перед публичной публикацией добавьте в проект файл `LICENSE`.
