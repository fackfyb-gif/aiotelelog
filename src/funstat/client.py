"""Typed async client for the funstat OpenAPI."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterable
from typing import Any, TypeVar

import httpx
from pydantic import TypeAdapter, ValidationError

from .models import (
    ApiResponse,
    AppProblem,
    ChatInfoExt,
    CommonGroupInfo,
    GiftRelation,
    GroupMember,
    Paged,
    ResolvedUser,
    StickerInfo,
    UserChatInfo,
    UserMsg,
    UserNameInfo,
    UserResult,
    UserStats,
    UserStatsMin,
    UsernameUsage,
    WhoWroteText,
)

T = TypeVar("T")


class FunstatError(Exception):
    """Base exception for transport and response parsing failures."""


class ProblemError(FunstatError):
    """HTTP error returned by the API."""

    def __init__(self, status: int, problem: AppProblem | None = None):
        self.status, self.problem = status, problem
        message = (problem.detail if problem else None) or (problem.title if problem else None)
        super().__init__(message or f"HTTP {status}")


def _page_args(page: int, page_size: int) -> dict[str, int]:
    if page < 1 or page_size < 1:
        raise ValueError("page and page_size must be positive")
    return {"page": page, "pageSize": page_size}


def _query(values: dict[str, Any]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for key, value in values.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            result.extend((key, str(item)) for item in value)
        else:
            result.append((key, str(value).lower() if isinstance(value, bool) else str(value)))
    return result


class FunstatClient:
    """Async context-managed client.

    Parameters
    ----------
    base_url:
        API origin, for example ``https://api.example.com``.
    token:
        JWT token without the ``Bearer`` prefix.
    timeout:
        HTTPX timeout in seconds.
    http_client:
        Optional preconfigured client, useful for proxies and tests.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = 30.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._owns_client = http_client is None
        self._http = http_client or httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        self.groups = Groups(self)
        self.users = Users(self)
        self.text = Text(self)

    async def __aenter__(self) -> "FunstatClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def _get(self, path: str, model: Any, **params: Any) -> ApiResponse[Any]:
        try:
            response = await self._http.get(path, params=_query(params))
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            try:
                problem = AppProblem.model_validate(exc.response.json())
            except (ValueError, ValidationError):
                problem = None
            raise ProblemError(exc.response.status_code, problem) from exc
        except httpx.RequestError as exc:
            raise FunstatError(f"request failed: {exc}") from exc
        try:
            return TypeAdapter(ApiResponse[model]).validate_python(response.json())
        except (ValueError, ValidationError) as exc:
            raise FunstatError("server returned an invalid response") from exc

    async def _plain(self, path: str, model: type[T], **params: Any) -> T:
        try:
            response = await self._http.get(path, params=_query(params))
            response.raise_for_status()
            return TypeAdapter(model).validate_python(response.json())
        except httpx.HTTPStatusError as exc:
            try:
                problem = AppProblem.model_validate(exc.response.json())
            except (ValueError, ValidationError):
                problem = None
            raise ProblemError(exc.response.status_code, problem) from exc
        except httpx.RequestError as exc:
            raise FunstatError(f"request failed: {exc}") from exc
        except (ValueError, ValidationError) as exc:
            raise FunstatError("server returned an invalid response") from exc


class Groups:
    def __init__(self, client: FunstatClient) -> None:
        self._client = client

    async def common_groups(self, ids: Iterable[int]) -> ApiResponse[list[ChatInfoExt]]:
        return await self._client._get("/api/v1/groups/common_groups", list[ChatInfoExt], id=list(ids))

    async def get(self, group_id: int) -> ApiResponse[Any]:
        return await self._client._get(f"/api/v1/groups/{group_id}", Any)

    async def members(self, group_id: int) -> ApiResponse[list[GroupMember]]:
        return await self._client._get(f"/api/v1/groups/{group_id}/members", list[GroupMember])


class Users:
    def __init__(self, client: FunstatClient) -> None:
        self._client = client

    async def gifts_relation(self, user_id: int, page: int, page_size: int) -> ApiResponse[list[GiftRelation]]:
        return await self._client._get(
            f"/api/v1/users/{user_id}/gifts_relation", list[GiftRelation], **_page_args(page, page_size)
        )

    async def stickers(self, user_id: int) -> ApiResponse[list[StickerInfo]]:
        return await self._client._get(f"/api/v1/users/{user_id}/stickers", list[StickerInfo])

    async def common_groups_stat(self, user_id: int) -> ApiResponse[list[CommonGroupInfo]]:
        return await self._client._get(f"/api/v1/users/{user_id}/common_groups_stat", list[CommonGroupInfo])

    async def reputation(self, user_id: int | None = None) -> ApiResponse[Any]:
        return await self._client._get("/api/v1/users/reputation", Any, id=user_id)

    async def name_usage(self, name: str, page: int, page_size: int) -> ApiResponse[Paged[UserResult]]:
        return await self._client._get(
            "/api/v1/users/name_usage", Paged[UserResult], name=name, **_page_args(page, page_size)
        )

    async def username_usage(self, username: str) -> ApiResponse[UsernameUsage]:
        return await self._client._get("/api/v1/users/username_usage", UsernameUsage, username=username)

    async def resolve_username(self, names: Iterable[str]) -> ApiResponse[list[ResolvedUser]]:
        return await self._client._get("/api/v1/users/resolve_username", list[ResolvedUser], name=list(names))

    async def stats_min(self, user_id: int) -> ApiResponse[UserStatsMin]:
        return await self._client._get(f"/api/v1/users/{user_id}/stats_min", UserStatsMin)

    async def stats(self, user_id: int) -> ApiResponse[UserStats]:
        return await self._client._get(f"/api/v1/users/{user_id}/stats", UserStats)

    async def basic_info_by_id(self, ids: Iterable[int]) -> ApiResponse[list[ResolvedUser]]:
        return await self._client._get("/api/v1/users/basic_info_by_id", list[ResolvedUser], id=list(ids))

    async def groups_count(self, user_id: int, only_msg: bool | None = None) -> int:
        return await self._client._plain(f"/api/v1/users/{user_id}/groups_count", int, onlyMsg=only_msg)

    async def messages(
        self,
        user_id: int,
        page: int,
        page_size: int,
        *,
        group_id: int | None = None,
        text_contains: str | None = None,
        media_code: int | None = None,
    ) -> ApiResponse[list[UserMsg]]:
        return await self._client._get(
            f"/api/v1/users/{user_id}/messages",
            list[UserMsg],
            group_id=group_id,
            text_contains=text_contains,
            media_code=media_code,
            **_page_args(page, page_size),
        )

    async def messages_count(self, user_id: int) -> int:
        return await self._client._plain(f"/api/v1/users/{user_id}/messages_count", int)

    async def groups(self, user_id: int) -> ApiResponse[list[UserChatInfo]]:
        return await self._client._get(f"/api/v1/users/{user_id}/groups", list[UserChatInfo])

    async def names(self, user_id: int) -> ApiResponse[list[UserNameInfo]]:
        return await self._client._get(f"/api/v1/users/{user_id}/names", list[UserNameInfo])

    async def usernames(self, user_id: int) -> ApiResponse[list[UserNameInfo]]:
        return await self._client._get(f"/api/v1/users/{user_id}/usernames", list[UserNameInfo])

    async def iter_messages(
        self,
        user_id: int,
        *,
        page_size: int = 100,
        group_id: int | None = None,
        text_contains: str | None = None,
        media_code: int | None = None,
    ) -> AsyncIterator[UserMsg]:
        page = 1
        while True:
            result = await self.messages(
                user_id,
                page,
                page_size,
                group_id=group_id,
                text_contains=text_contains,
                media_code=media_code,
            )
            for item in result.data or []:
                yield item
            paging = result.paging
            if not paging or page >= paging.total_pages:
                break
            page += 1


class Text:
    def __init__(self, client: FunstatClient) -> None:
        self._client = client

    async def search(self, input: str, page: int, page_size: int) -> ApiResponse[Paged[WhoWroteText]]:
        return await self._client._get(
            "/api/v1/text/search", Paged[WhoWroteText], input=input, **_page_args(page, page_size)
        )

    async def iter_search(self, input: str, *, page_size: int = 100) -> AsyncIterator[WhoWroteText]:
        page = 1
        while True:
            result = await self.search(input, page, page_size)
            for item in (result.data.data if result.data else []):
                yield item
            paging = result.data
            if not paging or not paging.total_pages or page >= paging.total_pages:
                break
            page += 1
