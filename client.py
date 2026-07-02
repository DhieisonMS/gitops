import os
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import requests


class GithubClient:
    DEFAULT_BASE_URL = "https://api.github.com"
    TOKEN_ENV_NAMES = ("GITHUB_TOKEN", "GH_TOKEN")

    def __init__(self, token: str | None = None, base_url: str | None = None):
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.token = self.resolve_token(token)
        self.session = self.create_session()

    @classmethod
    def load_env(cls) -> None:
        try:
            from dotenv import load_dotenv
        except ImportError:
            return

        load_dotenv()

    @classmethod
    def resolve_token(cls, token: str | None = None) -> str:
        if token:
            return token

        for env_name in cls.TOKEN_ENV_NAMES:
            value = os.getenv(env_name)
            if value:
                return value

        raise RuntimeError("Defina GITHUB_TOKEN ou GH_TOKEN para autenticar no GitHub.")

    def create_session(self) -> "requests.Session":
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("Instale a dependencia requests para usar o client do GitHub.") from exc

        session = requests.Session()
        session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        return session
