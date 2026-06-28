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

    def push(self, local_path: Path, remote_name: str) -> str:
        if not local_path.is_file():
            raise RegistryError(f"artifact not found: {local_path}")
        url = f"{self._base_url}/{self._repo}/{remote_name}"
        response = requests.put(
            url,
            data=local_path.read_bytes(),
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=60,
        )
        if response.status_code >= 400:
            raise RegistryError(f"push failed: {response.status_code} {response.text}")
        logger.info("pushed artifact to %s", url)
        return url
