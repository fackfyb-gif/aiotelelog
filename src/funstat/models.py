"""Pydantic v2 models generated from swagger.json."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Model(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class TechInfo(Model):
    request_cost: float
    current_balance: float = Field(alias="current_ballance")
    request_duration: str


class Paging(Model):
    total: int
    current_page: int = Field(alias="currentPage")
    page_size: int = Field(alias="pageSize")
    total_pages: int = Field(alias="totalPages")


class ApiResponse(Model, Generic[T]):
    success: bool
    tech: TechInfo
    data: T | None = None
    paging: Paging | None = None


class AppProblem(Model):
    detail: str | None = None
    instance: str | None = None
    status: int | None = None
    title: str | None = None
    type: str | None = None
    method: str | None = None
    app_version: str | None = Field(default=None, alias="appVersion")
    date_time: datetime | None = Field(default=None, alias="dateTime")


class ProblemDetails(Model):
    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None


class ChatInfo(Model):
    id: int
    title: str
    is_private: bool = Field(alias="isPrivate")
    username: str | None = None


class ChatInfoExt(Model):
    id: int
    title: str
    is_private: bool = Field(alias="isPrivate")
    is_channel: bool = Field(alias="isChannel")
    username: str | None = None
    link: str | None = None


class ResolvedUser(Model):
    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool
    is_bot: bool
    has_premium: bool | None = None


class GroupMember(Model):
    id: int | None = None
    username: str | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_admin: bool | None = None
    is_active: bool | None = None
    today_msg: int | None = None
    has_prem: bool | None = None
    has_photo: bool | None = None
    dc_id: int | None = None


class GiftRelation(Model):
    last_gift_date: datetime | None = None
    from_user_id: int | None = None
    from_first_name: str | None = None
    from_last_name: str | None = None
    from_main_username: str | None = Field(default=None, alias="from_mainUsername")
    from_is_active: bool | None = None
    to_user_id: int | None = None
    to_first_name: str | None = None
    to_last_name: str | None = None
    to_main_username: str | None = Field(default=None, alias="to_mainUsername")
    to_is_active: bool | None = None


class StickerInfo(Model):
    sticker_set_id: int = Field(alias="sticker_set_id")
    last_seen: date
    min_seen: date
    resolved: datetime | None = None
    title: str | None = None
    short_name: str | None = None
    stickers_count: int | None = None


class CommonGroupInfo(Model):
    user_id: int
    common_groups: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    is_user_active: bool


class UserResult(Model):
    id: int
    username: str | None = Field(default=None, alias="userName")
    first_name: str
    last_name: str | None = None
    name: str | None = None
    is_bot: bool


class Paged(Model, Generic[T]):
    total: int
    data: list[T]
    is_last_page: bool | None = Field(default=None, alias="isLastPage")
    page_size: int | None = Field(default=None, alias="pageSize")
    current_page: int | None = Field(default=None, alias="currentPage")
    total_pages: int | None = Field(default=None, alias="totalPages")
    is_sliding: bool | None = Field(default=None, alias="isSliding")


class UserNameInfo(Model):
    date_time: datetime = Field(alias="date_time")
    name: str


class UserMsg(Model):
    date: datetime
    message_id: int = Field(alias="messageId")
    reply_to_message_id: int | None = Field(default=None, alias="replyToMessageId")
    media_code: int | None = Field(default=None, alias="mediaCode")
    media_name: str | None = Field(default=None, alias="mediaName")
    text: str
    group: ChatInfo


class UserChatInfo(Model):
    chat: ChatInfo | None = None
    last_message_id: int | None = Field(default=None, alias="lastMessageId")
    messages_count: int | None = Field(default=None, alias="messagesCount")
    last_message: datetime | None = Field(default=None, alias="lastMessage")
    first_message: datetime | None = Field(default=None, alias="firstMessage")
    is_admin: bool | None = Field(default=None, alias="isAdmin")
    is_left: bool | None = Field(default=None, alias="isLeft")


class UserStatsMin(Model):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    is_bot: bool
    is_active: bool
    first_msg_date: datetime | None = None
    last_msg_date: datetime | None = None
    total_msg_count: int
    msg_in_groups_count: int
    adm_in_groups: int
    usernames_count: int
    names_count: int
    total_groups: int


class UserStats(UserStatsMin):
    is_cyrillic_primary: bool | None = None
    lang_code: str | None = None
    unique_percent: float | None = None
    circle_count: int
    voice_count: int
    reply_percent: float
    media_percent: float
    link_percent: float
    favorite_chat: ChatInfo | None = None
    media_usage: str | None = None
    stars_val: int | None = None
    personal_channel_id: int | None = None
    gift_count: int | None = None
    stars_level: int | None = None
    birth_day: int | None = None
    birth_month: int | None = None
    birth_year: int | None = None
    about: str | None = None


class UsernameUsage(Model):
    actual_users: list[ResolvedUser] | None = Field(default=None, alias="actualUsers")
    usage_by_users_in_the_past: list[ResolvedUser] | None = Field(
        default=None, alias="usageByUsersInThePast"
    )
    actual_groups_or_channels: list[ChatInfoExt] | None = Field(
        default=None, alias="actualGroupsOrChannels"
    )
    mention_by_channel_or_group_desc: list[ChatInfoExt] | None = Field(
        default=None, alias="mentionByChannelOrGroupDesc"
    )


class WhoWroteText(Model):
    message_id: int | None = None
    user_id: int | None = None
    date: datetime | None = None
    name: str | None = None
    username: str | None = None
    is_active: bool | None = None
    group: ChatInfoExt | None = None
    text: str | None = None


__all__ = [
    "ApiResponse", "AppProblem", "ChatInfo", "ChatInfoExt", "CommonGroupInfo",
    "GiftRelation", "GroupMember", "Paged", "Paging", "ProblemDetails",
    "ResolvedUser", "StickerInfo", "TechInfo", "UserChatInfo", "UserMsg",
    "UserNameInfo", "UserResult", "UserStats", "UserStatsMin", "UsernameUsage",
    "WhoWroteText",
]
