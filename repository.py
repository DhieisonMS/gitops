from typing import Any

from ky.integrations.github.client import GithubClient


class githubIntegrationRepositories:
    def __init__(self, token: str | None = None, base_url: str | None = None):
        self.client = GithubClient(token=token, base_url=base_url)
        self.session = self.client.session
        self.base_url = self.client.base_url

    def create_repository(
        self,
        name: str,
        description: str | None = None,
        visibility: str = "private",
        organization: str | None = None,
        auto_init: bool = False,
    ) -> dict[str, Any]:
        if visibility == "internal" and not organization:
            raise RuntimeError("Repositorios internos so podem ser criados em organizacoes enterprise.")

        url = (
            f"{self.base_url}/orgs/{organization}/repos"
            if organization
            else f"{self.base_url}/user/repos"
        )
        payload: dict[str, Any] = {
            "name": name,
            "visibility": visibility,
            "auto_init": auto_init,
        }

        if description:
            payload["description"] = description

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def delete_repository(
        self,
        name: str,
        organization: str | None = None,
    ) -> dict[str, Any]:
        owner = organization or self.get_authenticated_user()
        url = f"{self.base_url}/repos/{owner}/{name}"

        response = self.session.delete(url)
        response.raise_for_status()
        return {"full_name": f"{owner}/{name}"}

    def get_authenticated_user(self) -> str:
        response = self.session.get(f"{self.base_url}/user")
        response.raise_for_status()
        return response.json()["login"]

    def list_user_repositories(self) -> list[str]:
        url = f"{self.base_url}/user/repos"
        params: dict[str, Any] | None = {
            "per_page": 100,
            "affiliation": "owner,collaborator,organization_member",
        }
        repositories: list[str] = []

        while url:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            repositories.extend(repo["full_name"] for repo in response.json())
            url = response.links.get("next", {}).get("url")
            params = None

        return repositories

    def list_repositories(self, organization: str) -> list[str]:
        url = f"{self.base_url}/orgs/{organization}/repos"
        params: dict[str, Any] | None = {"per_page": 100, "type": "all"}
        repositories: list[str] = []

        while url:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            repositories.extend(repo["full_name"] for repo in response.json())
            url = response.links.get("next", {}).get("url")
            params = None

        return repositories


GithubIntegrationRepositories = githubIntegrationRepositories
