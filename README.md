<p align="center">
  <img src="assets/logo.svg" alt="aiotelelog" width="640">
</p>

<h1 align="center">aiotelelog</h1>

<p align="center">
  A typed, asynchronous Python client for the funstat Telegram-data API.
</p>

<p align="center">
  <a href="https://github.com/loopy-iri/aiotelelog"><img src="https://img.shields.io/github/repo-size/loopy-iri/aiotelelog" alt="Repository size"></a>
  <a href="https://github.com/loopy-iri/aiotelelog/releases"><img src="https://img.shields.io/github/v/release/loopy-iri/aiotelelog?display_name=tag" alt="Latest release"></a>
  <a href="https://github.com/loopy-iri/aiotelelog/blob/main/LICENSE"><img src="https://img.shields.io/github/license/loopy-iri/aiotelelog" alt="License"></a>
</p>

`aiotelelog` is an async, strongly typed and Pydantic-based client for the
`funstat` API. It covers all 20 endpoints described by `swagger.json`, including
pagination, request-cost metadata and RFC 7807-style problem responses.

## Features

- Python 3.10+
- `httpx.AsyncClient` with `async with` lifecycle support
- Pydantic v2 models for the Swagger schemas
- Complete public type hints for every endpoint
- Bearer JWT authentication
- Repeated query parameters for arrays, such as `id=1&id=2`
- Typed pagination and async iterators for messages and text search
- Dedicated network and HTTP exceptions
- Tokens are never written to logs

## Installation

From PyPI:

```bash
python -m pip install funstat-client
```

From source:

```bash
git clone https://github.com/loopy-iri/aiotelelog.git
cd aiotelelog
python -m pip install -e .
```

## Getting an API token

The Swagger contract does not define token issuance. The service entry point
for obtaining credentials is `/api`.

1. Open the service's `/api` page, for example
   `https://YOUR_API_HOST/api`.
2. Follow the registration or token-issuance instructions shown by the service.
3. If Telegram verification is requested, contact
   [`@funwordsffbot`](https://t.me/funwordsffbot) and follow the commands shown
   by the bot.
4. Store the token only in a secret manager or environment variable:

```bash
export FUNSTAT_BASE_URL="https://YOUR_API_HOST"
export FUNSTAT_TOKEN="paste-token-here"
```

The library exposes the same entry points without pretending to know an
undocumented payload:

```python
from funstat import token_guide

guide = token_guide("https://YOUR_API_HOST")
print(guide.api_url)       # https://YOUR_API_HOST/api
print(guide.telegram_url)  # https://t.me/funwordsffbot
print(guide.instructions())
```

The SDK intentionally does not send a guessed token-issuance request because
that protocol is not present in `swagger.json`.

## Quick start

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
            print(f"request cost: {result.tech.request_cost}")

        groups = await api.users.groups(123456789)
        for item in groups.data or []:
            print(item.chat.title if item.chat else "<unknown>")


asyncio.run(main())
```

## Pagination

Control pages manually:

```python
page = await api.users.messages(123456789, page=1, page_size=50)
for message in page.data or []:
    print(message.message_id, message.text)
```

Or iterate through every page:

```python
async for message in api.users.iter_messages(123456789, page_size=100):
    print(message.message_id)

async for match in api.text.iter_search("python", page_size=50):
    print(match.user_id, match.group)
```

Use iterators deliberately for paid endpoints because they may issue many
requests.

## SDK resources

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

## Responses and models

Most endpoints return a generic envelope:

```python
ApiResponse[T](
    success=True,
    tech=TechInfo(...),
    data=T | None,
    paging=Paging | None,
)
```

Public models can be imported directly:

```python
from funstat import ApiResponse, UserMsg, UserStats

payload: ApiResponse[UserStats]
```

Pydantic aliases map API names to Python names. For example, `pageSize` is
available as `page_size`, and the API's `current_ballance` is exposed as
`current_balance`.

## Error handling

```python
from funstat import FunstatError, ProblemError

try:
    result = await api.users.stats(123)
except ProblemError as exc:
    print(exc.status)
    print(exc.problem)
except FunstatError as exc:
    print(f"request failed: {exc}")
```

`ProblemError` represents HTTP errors such as `401`, `403` and `500`.
The parsed `AppProblem` is available as `exc.problem`.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m build
```

Tests use `httpx.MockTransport`; no real API token or network connection is
required.

## Documentation

- [Complete English API documentation](docs/API.en.md)
- [مستندات کامل فارسی](docs/API.fa.md)
- [API documentation index](docs/API.md)
- [Library development plan](docs/PYTHON_LIBRARY_PLAN.md)

## Git and releases

Initial setup:

```bash
git remote add origin https://github.com/loopy-iri/aiotelelog.git
git branch -M main
git add .
git commit -m "feat: add typed async funstat client"
git push -u origin main
```

Create a release tag:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

With GitHub CLI:

```bash
gh auth login
gh release create v0.1.0 --title "v0.1.0" --generate-notes
```

For the next release, update `pyproject.toml` and `CHANGELOG.md`, then run:

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main --follow-tags
```

## License

Add a `LICENSE` file before publishing the project publicly.

---

# مستندات فارسی

`aiotelelog` یک کلاینت asynchronous، تایپ‌شده و مبتنی بر Pydantic برای API
داده‌های تلگرام `funstat` است. این کتابخانه هر ۲۰ endpoint تعریف‌شده در
`swagger.json`، pagination، هزینه‌ی درخواست و خطاهای API را پوشش می‌دهد.

## امکانات

- Python 3.10+
- `httpx.AsyncClient` و پشتیبانی کامل از `async with`
- مدل‌های Pydantic v2 برای schemaهای Swagger
- type hint کامل برای endpointهای عمومی
- احراز هویت Bearer JWT
- پشتیبانی از آرایه‌های query مانند `id=1&id=2`
- pagination و async iterator برای پیام‌ها و جست‌وجوی متن
- exceptionهای مشخص برای خطاهای شبکه و HTTP
- عدم ثبت token در log

## نصب

از PyPI:

```bash
python -m pip install funstat-client
```

از سورس:

```bash
git clone https://github.com/loopy-iri/aiotelelog.git
cd aiotelelog
python -m pip install -e .
```

## دریافت API token

قرارداد صدور token در Swagger تعریف نشده است؛ مسیر ورود سرویس `/api` است:

1. صفحه‌ی `/api` سرویس را باز کنید، مانند `https://YOUR_API_HOST/api`.
2. مراحل ثبت‌نام یا صدور token را که سرویس نمایش می‌دهد انجام دهید.
3. اگر تأیید Telegram لازم بود، به
   [`@funwordsffbot`](https://t.me/funwordsffbot) پیام بدهید و commandهایی را
   که ربات نمایش می‌دهد اجرا کنید.
4. token را در secret manager یا environment variable نگه دارید:

```bash
export FUNSTAT_BASE_URL="https://YOUR_API_HOST"
export FUNSTAT_TOKEN="paste-token-here"
```

کتابخانه لینک‌های این flow را نیز در اختیار می‌گذارد:

```python
from funstat import token_guide

guide = token_guide("https://YOUR_API_HOST")
print(guide.api_url)       # https://YOUR_API_HOST/api
print(guide.telegram_url)  # https://t.me/funwordsffbot
print(guide.instructions())
```

SDK عمداً payload یا command ساختگی برای صدور token ارسال نمی‌کند، چون این
قرارداد در `swagger.json` تعریف نشده است.

## شروع سریع

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
            print(f"هزینه درخواست: {result.tech.request_cost}")


asyncio.run(main())
```

## صفحه‌بندی

کنترل دستی صفحه‌ها:

```python
page = await api.users.messages(123456789, page=1, page_size=50)
for message in page.data or []:
    print(message.message_id, message.text)
```

یا پیمایش همه‌ی صفحه‌ها:

```python
async for message in api.users.iter_messages(123456789, page_size=100):
    print(message.message_id)

async for match in api.text.iter_search("python", page_size=50):
    print(match.user_id, match.group)
```

برای endpointهای هزینه‌دار، iterator را فقط زمانی استفاده کنید که به تمام
صفحه‌ها نیاز دارید.

## منابع SDK

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

## پاسخ‌ها و مدل‌ها

بیشتر endpointها پاسخ generic زیر را برمی‌گردانند:

```python
ApiResponse[T](
    success=True,
    tech=TechInfo(...),
    data=T | None,
    paging=Paging | None,
)
```

مدل‌های عمومی را می‌توان مستقیماً import کرد:

```python
from funstat import ApiResponse, UserMsg, UserStats

payload: ApiResponse[UserStats]
```

نام‌های JSON با aliasهای Pydantic به نام‌های Python تبدیل می‌شوند؛ مثلاً
`pageSize` به `page_size` و `current_ballance` به `current_balance` تبدیل می‌شود.

## مدیریت خطا

```python
from funstat import FunstatError, ProblemError

try:
    result = await api.users.stats(123)
except ProblemError as exc:
    print(exc.status)
    print(exc.problem)
except FunstatError as exc:
    print(f"خطا در درخواست: {exc}")
```

`ProblemError` برای خطاهای HTTP مانند `401`، `403` و `500` است و مدل parse‌شده‌ی
`AppProblem` در `exc.problem` قرار دارد.

## توسعه و تست

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m build
```

تست‌ها با `httpx.MockTransport` اجرا می‌شوند و به token یا اتصال واقعی نیاز
ندارند.

## مستندات

- [مستندات کامل فارسی](docs/API.fa.md)
- [Complete English documentation](docs/API.en.md)
- [فهرست مستندات API](docs/API.md)
- [پلن توسعه کتابخانه](docs/PYTHON_LIBRARY_PLAN.md)

## Git و انتشار

تنظیم اولیه:

```bash
git remote add origin https://github.com/loopy-iri/aiotelelog.git
git branch -M main
git add .
git commit -m "feat: add typed async funstat client"
git push -u origin main
```

ساخت release:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

با GitHub CLI:

```bash
gh auth login
gh release create v0.1.0 --title "v0.1.0" --generate-notes
```

برای نسخه‌ی بعدی، `pyproject.toml` و `CHANGELOG.md` را به‌روزرسانی کنید:

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main --follow-tags
```

## مجوز

قبل از انتشار عمومی، فایل `LICENSE` را به پروژه اضافه کنید.
