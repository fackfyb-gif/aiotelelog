"""Token acquisition guidance exposed by the library."""

from dataclasses import dataclass

API_TOKEN_PATH = "/api"
TELEGRAM_BOT_USERNAME = "funwordsffbot"


@dataclass(frozen=True, slots=True)
class TokenGuide:
    """Links and instructions for obtaining a funstat API token.

    The Swagger contract does not define token issuance, so this helper only
    exposes the documented entry points and never guesses a request payload.
    """

    base_url: str
    api_path: str = API_TOKEN_PATH
    telegram_bot: str = TELEGRAM_BOT_USERNAME

    @property
    def api_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.api_path}"

    @property
    def telegram_url(self) -> str:
        return f"https://t.me/{self.telegram_bot.lstrip('@')}"

    def instructions(self) -> str:
        return (
            f"Open {self.api_url} to start API-token registration, then use "
            f"@{self.telegram_bot.lstrip('@')} for Telegram verification or "
            "the remaining steps shown by the service."
        )


def token_guide(base_url: str) -> TokenGuide:
    """Return links for the service's `/api` token-registration flow."""

    return TokenGuide(base_url)

