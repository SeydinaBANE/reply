import logging
from pathlib import Path

import requests

from pipeline.errors import RegistryError

logger = logging.getLogger(__name__)


class ArtifactRegistry:
    def __init__(self, base_url: str, repo: str, token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._repo = repo
        self._token = token

    def _url(self, remote_name: str) -> str:
        return f"{self._base_url}/{self._repo}/{remote_name}"

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    def push(self, local_path: Path, remote_name: str) -> str:
        if not local_path.is_file():
            raise RegistryError(f"artifact not found: {local_path}")
        response = requests.put(
            self._url(remote_name),
            data=local_path.read_bytes(),
            headers=self._headers(),
            timeout=60,
        )
        if response.status_code >= 400:
            raise RegistryError(f"push failed: {response.status_code} {response.text}")
        logger.info("pushed artifact to %s", self._url(remote_name))
        return self._url(remote_name)

    def pull(self, remote_name: str, dest: Path) -> Path:
        response = requests.get(self._url(remote_name), headers=self._headers(), timeout=60)
        if response.status_code >= 400:
            raise RegistryError(f"pull failed: {response.status_code} {response.text}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(response.content)
        logger.info("pulled artifact to %s", dest)
        return dest
