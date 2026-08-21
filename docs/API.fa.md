# مستندات فارسی SDK و API

این پروژه یک SDK کاملاً asynchronous برای API سرویس `funstat` است. قرارداد از
`swagger.json` با OpenAPI `3.0.4` استخراج شده و مدل‌های پاسخ با Pydantic v2
اعتبارسنجی می‌شوند.

## نصب

```bash
python -m pip install funstat-client
```

یا برای توسعه‌ی محلی:

```bash
python -m pip install -e .
```

وابستگی‌های runtime فقط `httpx` و `pydantic` هستند.

## شروع سریع

```python
import asyncio
from funstat import FunstatClient


async def main() -> None:
    async with FunstatClient(
        base_url="https://api.example.com",
        token="YOUR_JWT",
    ) as api:
        result = await api.users.stats_min(123456789)
        if result.data:
            print(result.data.first_name, result.data.total_msg_count)
            print("cost:", result.tech.request_cost)


asyncio.run(main())
```

`base_url` در Swagger اعلام نشده است و باید از مالک سرویس دریافت شود. توکن فقط
خود JWT است؛ SDK هدر `Authorization: Bearer ...` را می‌سازد.

## طراحی async و typeها

تمام endpointها `async def` هستند و باید با `await` فراخوانی شوند. پاسخ‌های
envelope با مدل generic زیر parse می‌شوند:

```python
ApiResponse[T](
    success: bool,
    tech: TechInfo,
    data: T | None,
    paging: Paging | None,
)
```

برای نمونه، نوع خروجی `api.users.stats_min(id)` برابر
`ApiResponse[UserStatsMin]` و نوع خروجی `api.groups.members(id)` برابر
`ApiResponse[list[GroupMember]]` است. مقادیر JSON با aliasهای API (مثل
`currentPage`, `pageSize`, `isPrivate`) در مدل Python به snake_case تبدیل می‌شوند.

## منابع و endpointها

### `api.groups`

| متد SDK | مسیر | نوع خروجی | هزینه‌ی اعلام‌شده |
|---|---|---|---:|
| `common_groups(ids)` | `GET /api/v1/groups/common_groups` | `ApiResponse[list[ChatInfoExt]]` | 0.5 |
| `get(group_id)` | `GET /api/v1/groups/{id}` | `ApiResponse[Any]` | 0.01 |
| `members(group_id)` | `GET /api/v1/groups/{id}/members` | `ApiResponse[list[GroupMember]]` | 15 |

`ids` به‌صورت پارامتر تکرارشونده (`id=1&id=2`) ارسال می‌شود.

### `api.users`

| متد SDK | مسیر | نوع خروجی | هزینه |
|---|---|---|---:|
| `gifts_relation(user_id, page, page_size)` | `GET /api/v1/users/{id}/gifts_relation` | `ApiResponse[list[GiftRelation]]` | 5 در صورت بیش از ۵ رابطه |
| `stickers(user_id)` | `GET /api/v1/users/{id}/stickers` | `ApiResponse[list[StickerInfo]]` | 1 در صورت یافتن |
| `common_groups_stat(user_id)` | `GET /api/v1/users/{id}/common_groups_stat` | `ApiResponse[list[CommonGroupInfo]]` | 5 |
| `reputation(user_id=None)` | `GET /api/v1/users/reputation` | `ApiResponse[Any]` | رایگان |
| `name_usage(name, page, page_size)` | `GET /api/v1/users/name_usage` | `ApiResponse[Paged[UserResult]]` | اعلام نشده |
| `username_usage(username)` | `GET /api/v1/users/username_usage` | `ApiResponse[UsernameUsage]` | 0.1 |
| `resolve_username(names)` | `GET /api/v1/users/resolve_username` | `ApiResponse[list[ResolvedUser]]` | 0.1 برای هر موفقیت |
| `stats_min(user_id)` | `GET /api/v1/users/{id}/stats_min` | `ApiResponse[UserStatsMin]` | رایگان |
| `stats(user_id)` | `GET /api/v1/users/{id}/stats` | `ApiResponse[UserStats]` | 1 |
| `basic_info_by_id(ids)` | `GET /api/v1/users/basic_info_by_id` | `ApiResponse[list[ResolvedUser]]` | 0.1 برای هر موفقیت |
| `groups_count(user_id, only_msg=None)` | `GET /api/v1/users/{id}/groups_count` | `int` | رایگان |
| `messages(user_id, page, page_size, ...)` | `GET /api/v1/users/{id}/messages` | `ApiResponse[list[UserMsg]]` | 10 در شرایط اعلام‌شده |
| `messages_count(user_id)` | `GET /api/v1/users/{id}/messages_count` | `int` | رایگان |
| `groups(user_id)` | `GET /api/v1/users/{id}/groups` | `ApiResponse[list[UserChatInfo]]` | 5 |
| `names(user_id)` | `GET /api/v1/users/{id}/names` | `ApiResponse[list[UserNameInfo]]` | 3 |
| `usernames(user_id)` | `GET /api/v1/users/{id}/usernames` | `ApiResponse[list[UserNameInfo]]` | 3 |

پارامترهای `page` و `page_size` باید مثبت باشند. در `messages` فیلترهای اختیاری
`group_id`، `text_contains` و `media_code` نیز موجودند.

### `api.text`

| متد SDK | مسیر | نوع خروجی | هزینه |
|---|---|---|---:|
| `search(input, page, page_size)` | `GET /api/v1/text/search` | `ApiResponse[Paged[WhoWroteText]]` | 0.1 |

## pagination و iterator

برای دریافت تدریجی نتایج و جلوگیری از درخواست‌های ناخواسته:

```python
async for message in api.users.iter_messages(123, page_size=100):
    print(message.message_id, message.text)

async for match in api.text.iter_search("python", page_size=50):
    print(match.user_id, match.group)
```

این iteratorها همه‌ی صفحات را می‌خوانند؛ برای endpointهای هزینه‌دار فقط در صورت
نیاز از آن‌ها استفاده کنید.

## مدل‌های Pydantic

مدل‌های عمومی از `funstat` قابل import هستند:

```python
from funstat import UserStats, UserMsg, ApiResponse

payload: ApiResponse[UserStats]
```

مدل‌ها شامل `TechInfo`, `Paging`, `ChatInfo`, `ChatInfoExt`, `ResolvedUser`,
`GroupMember`, `GiftRelation`, `StickerInfo`, `CommonGroupInfo`, `UserResult`,
`UserMsg`, `UserChatInfo`, `UserNameInfo`, `UserStatsMin`, `UserStats`,
`UsernameUsage` و `WhoWroteText` هستند.

## خطاها و lifecycle

- `FunstatError`: خطای شبکه یا JSON/مدل نامعتبر.
- `ProblemError`: پاسخ HTTP ناموفق؛ `status` و `problem: AppProblem | None`
  را در اختیار می‌گذارد.
- استفاده از `async with` باعث بسته‌شدن `httpx.AsyncClient` می‌شود. در صورت
  ساخت client بیرونی، می‌توان آن را با `http_client=` تزریق کرد.

```python
from funstat import ProblemError

try:
    async with FunstatClient(URL, TOKEN) as api:
        await api.users.stats(1)
except ProblemError as exc:
    print(exc.status, exc.problem)
```

Swagger برای پاسخ موفق `groups/{id}` و `users/reputation` schema مشخص نکرده؛
به همین دلیل SDK در این دو مورد `Any` برمی‌گرداند تا قرارداد ناقص سرویس را جعل
نکند.
