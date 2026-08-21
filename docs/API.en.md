# English SDK and API Documentation

This project is a fully asynchronous Python SDK for the `funstat` service.
The contract is derived from `swagger.json` (OpenAPI `3.0.4`) and responses are
validated with Pydantic v2.

## Installation

```bash
python -m pip install funstat-client
```

For local development:

```bash
python -m pip install -e .
```

The only runtime dependencies are `httpx` and `pydantic`.

## Quick start

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

The Swagger document does not define a `servers` URL; obtain `base_url` from the
service owner. Pass the raw JWT token; the SDK adds `Authorization: Bearer`.

## Async API and typing

Every endpoint is `async def` and must be awaited. Envelope responses use this
generic Pydantic model:

```python
ApiResponse[T](
    success: bool,
    tech: TechInfo,
    data: T | None,
    paging: Paging | None,
)
```

For example, `api.users.stats_min(id)` returns
`ApiResponse[UserStatsMin]`, while `api.groups.members(id)` returns
`ApiResponse[list[GroupMember]]`. API aliases such as `currentPage`, `pageSize`
and `isPrivate` are exposed as Python snake_case attributes.

## Resources and endpoints

### `api.groups`

| SDK method | Path | Return type | Documented cost |
|---|---|---|---:|
| `common_groups(ids)` | `GET /api/v1/groups/common_groups` | `ApiResponse[list[ChatInfoExt]]` | 0.5 |
| `get(group_id)` | `GET /api/v1/groups/{id}` | `ApiResponse[Any]` | 0.01 |
| `members(group_id)` | `GET /api/v1/groups/{id}/members` | `ApiResponse[list[GroupMember]]` | 15 |

`ids` are encoded as repeated query parameters (`id=1&id=2`).

### `api.users`

| SDK method | Path | Return type | Cost |
|---|---|---|---:|
| `gifts_relation(user_id, page, page_size)` | `GET /api/v1/users/{id}/gifts_relation` | `ApiResponse[list[GiftRelation]]` | 5 when more than 5 relations |
| `stickers(user_id)` | `GET /api/v1/users/{id}/stickers` | `ApiResponse[list[StickerInfo]]` | 1 when found |
| `common_groups_stat(user_id)` | `GET /api/v1/users/{id}/common_groups_stat` | `ApiResponse[list[CommonGroupInfo]]` | 5 |
| `reputation(user_id=None)` | `GET /api/v1/users/reputation` | `ApiResponse[Any]` | free |
| `name_usage(name, page, page_size)` | `GET /api/v1/users/name_usage` | `ApiResponse[Paged[UserResult]]` | unspecified |
| `username_usage(username)` | `GET /api/v1/users/username_usage` | `ApiResponse[UsernameUsage]` | 0.1 |
| `resolve_username(names)` | `GET /api/v1/users/resolve_username` | `ApiResponse[list[ResolvedUser]]` | 0.1 per success |
| `stats_min(user_id)` | `GET /api/v1/users/{id}/stats_min` | `ApiResponse[UserStatsMin]` | free |
| `stats(user_id)` | `GET /api/v1/users/{id}/stats` | `ApiResponse[UserStats]` | 1 |
| `basic_info_by_id(ids)` | `GET /api/v1/users/basic_info_by_id` | `ApiResponse[list[ResolvedUser]]` | 0.1 per success |
| `groups_count(user_id, only_msg=None)` | `GET /api/v1/users/{id}/groups_count` | `int` | free |
| `messages(user_id, page, page_size, ...)` | `GET /api/v1/users/{id}/messages` | `ApiResponse[list[UserMsg]]` | 10 under the documented condition |
| `messages_count(user_id)` | `GET /api/v1/users/{id}/messages_count` | `int` | free |
| `groups(user_id)` | `GET /api/v1/users/{id}/groups` | `ApiResponse[list[UserChatInfo]]` | 5 |
| `names(user_id)` | `GET /api/v1/users/{id}/names` | `ApiResponse[list[UserNameInfo]]` | 3 |
| `usernames(user_id)` | `GET /api/v1/users/{id}/usernames` | `ApiResponse[list[UserNameInfo]]` | 3 |

`page` and `page_size` must be positive. `messages` also accepts optional
`group_id`, `text_contains` and `media_code` filters.

### `api.text`

| SDK method | Path | Return type | Cost |
|---|---|---|---:|
| `search(input, page, page_size)` | `GET /api/v1/text/search` | `ApiResponse[Paged[WhoWroteText]]` | 0.1 |

## Pagination and iterators

Use iterators when you want all pages without manually managing page numbers:

```python
async for message in api.users.iter_messages(123, page_size=100):
    print(message.message_id, message.text)

async for match in api.text.iter_search("python", page_size=50):
    print(match.user_id, match.group)
```

Iterators fetch every page. Use them deliberately for paid endpoints.

## Pydantic models

Public models can be imported directly:

```python
from funstat import ApiResponse, UserMsg, UserStats

payload: ApiResponse[UserStats]
```

Available models include `TechInfo`, `Paging`, `ChatInfo`, `ChatInfoExt`,
`ResolvedUser`, `GroupMember`, `GiftRelation`, `StickerInfo`,
`CommonGroupInfo`, `UserResult`, `UserMsg`, `UserChatInfo`, `UserNameInfo`,
`UserStatsMin`, `UserStats`, `UsernameUsage` and `WhoWroteText`.

## Errors and lifecycle

- `FunstatError`: network, JSON or model-validation failure.
- `ProblemError`: an HTTP error; exposes `status` and
  `problem: AppProblem | None`.
- Use `async with` to close the internally-created `httpx.AsyncClient`. An
  externally configured client can be passed with `http_client=`.

```python
from funstat import ProblemError

try:
    async with FunstatClient(URL, TOKEN) as api:
        await api.users.stats(1)
except ProblemError as exc:
    print(exc.status, exc.problem)
```

Swagger does not define successful-response schemas for `groups/{id}` and
`users/reputation`. The SDK intentionally returns `Any` for those two methods
instead of inventing an undocumented contract.
