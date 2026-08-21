<p align="center">
  <img src="assets/logo.svg" alt="aiotelelog" width="640">
</p>

<h1 align="center">aiotelelog</h1>

<p align="center">
  Typed async Python client for the funstat Telegram-data API.
</p>

<p align="center">
  <a href="https://github.com/loopy-iri/aiotelelog"><img src="https://img.shields.io/github/repo-size/loopy-iri/aiotelelog" alt="Repository size"></a>
  <a href="https://github.com/loopy-iri/aiotelelog/releases"><img src="https://img.shields.io/github/v/release/loopy-iri/aiotelelog?display_name=tag" alt="Release"></a>
  <a href="https://github.com/loopy-iri/aiotelelog/blob/main/LICENSE"><img src="https://img.shields.io/github/license/loopy-iri/aiotelelog" alt="License"></a>
</p>

`aiotelelog` یک کلاینت asynchronous، تایپ‌شده و Pydantic-based برای API سرویس
`funstat` است. تمام endpointهای تعریف‌شده در `swagger.json`، پاسخ‌های
صفحه‌بندی‌شده، هزینه‌ی درخواست و خطاهای Problem Details را پوشش می‌دهد.

## امکانات

- Python 3.10+
- `httpx.AsyncClient` و پشتیبانی کامل از `async with`
- مدل‌های Pydantic v2 برای schemaهای Swagger
- type hint برای هر endpoint عمومی
- احراز هویت Bearer JWT
- پشتیبانی از آرایه‌های query مثل `id=1&id=2`
- pagination و async iterator برای پیام‌ها و جست‌وجوی متن
- exceptionهای مشخص برای خطای شبکه و HTTP
- بدون log کردن token

## نصب

```bash
python -m pip install funstat-client
```

نصب از سورس:

```bash
git clone https://github.com/loopy-iri/aiotelelog.git
cd aiotelelog
python -m pip install -e .
```

## دریافت API token

قرارداد صدور token در `swagger.json` تعریف نشده است؛ مسیر ورود سرویس `/api`
است. برای دریافت credential:

1. آدرس `/api` سرویس را باز کنید؛ مثلاً `https://YOUR_API_HOST/api`.
2. مراحل ثبت‌نام/صدور token را طبق صفحه‌ی سرویس انجام دهید.
3. اگر سرویس برای تأیید Telegram راهنمایی کرد، به ربات
   [`@funwordsffbot`](https://t.me/funwordsffbot) پیام بدهید و دقیقاً commandهایی
   را که ربات نمایش می‌دهد اجرا کنید.
4. token را فقط در secret manager یا environment variable نگه دارید:

```bash
export FUNSTAT_BASE_URL="https://YOUR_API_HOST"
export FUNSTAT_TOKEN="paste-token-here"
```

کتابخانه لینک‌های این flow را نیز type-safe در اختیار می‌گذارد:

```python
from funstat import token_guide

guide = token_guide("https://YOUR_API_HOST")
print(guide.api_url)       # .../api
print(guide.telegram_url)  # https://t.me/funwordsffbot
print(guide.instructions())
```

> SDK عمداً payload یا command ساختگی برای صدور token ارسال نمی‌کند، چون این
> قرارداد در Swagger وجود ندارد.

## استفاده

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
            print(f"cost={result.tech.request_cost}")

        groups = await api.users.groups(123456789)
        for item in groups.data or []:
            print(item.chat.title if item.chat else "<unknown>")


asyncio.run(main())
```

## صفحه‌بندی

برای کنترل دستی صفحات:

```python
page = await api.users.messages(123456789, page=1, page_size=50)
for message in page.data or []:
    print(message.message_id, message.text)
```

برای پیمایش همه‌ی صفحات:

```python
async for message in api.users.iter_messages(123456789, page_size=100):
    print(message.message_id)

async for match in api.text.iter_search("python", page_size=50):
    print(match.user_id, match.group)
```

برای endpointهای دارای هزینه، iterator را فقط زمانی استفاده کنید که واقعاً به
همه‌ی صفحات نیاز دارید.

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

پاسخ envelope معمولاً از نوع زیر است:

```python
ApiResponse[T](
    success=True,
    tech=TechInfo(...),
    data=T | None,
    paging=Paging | None,
)
```

مدل‌های عمومی از package قابل import هستند:

```python
from funstat import ApiResponse, UserStats, UserMsg

payload: ApiResponse[UserStats]
```

نام‌های JSON با aliasهای Pydantic به snake_case تبدیل می‌شوند؛ برای نمونه
`current_ballance` با نام API حفظ شده و در Python به `current_balance` دسترسی
دارد، و `pageSize` به `page_size` تبدیل می‌شود.

## خطاها

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

`ProblemError` برای statusهای HTTP مثل `401`, `403` و `500` است. اطلاعات
`AppProblem` در `exc.problem` قرار می‌گیرد.

## توسعه

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m build
```

تست‌ها با `httpx.MockTransport` بدون اتصال به API واقعی اجرا می‌شوند.

## مستندات

- [مستندات کامل فارسی](docs/API.fa.md)
- [Complete English documentation](docs/API.en.md)
- [API documentation index](docs/API.md)
- [Library plan](docs/PYTHON_LIBRARY_PLAN.md)

## انتشار و Git

تنظیم اولیه:

```bash
git remote add origin https://github.com/loopy-iri/aiotelelog.git
git branch -M main
git add .
git commit -m "feat: add typed async funstat client"
git push -u origin main
```

انتشار نسخه:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

برای release بعدی، نسخه‌ی `pyproject.toml` و changelog را تغییر دهید، commit
بزنید و tag جدید بسازید:

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main --follow-tags
```

## License

مجوز پروژه را قبل از انتشار عمومی در فایل `LICENSE` مشخص کنید.
