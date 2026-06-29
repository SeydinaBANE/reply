import logging
import time
from pathlib import Path

import requests

from pipeline.errors import RegistryError

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 1 << 20


class ArtifactRegistry:
    def __init__(
        self,
        base_url: str,
        repo: str,
        token: str,
        timeout: float = 60.0,
        max_attempts: int = 3,
        backoff_base: float = 0.5,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._repo = repo
        self._token = token
        self._timeout = timeout
        self._max_attempts = max_attempts
        self._backoff_base = backoff_base

    def _url(self, remote_name: str) -> str:
        return f"{self._base_url}/{self._repo}/{remote_name}"

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    def _sleep(self, attempt: int) -> None:
        time.sleep(self._backoff_base * (2 ** (attempt - 1)))

    def push(self, local_path: Path, remote_name: str) -> str:
        if not local_path.is_file():
            raise RegistryError(f"artifact not found: {local_path}")
        url = self._url(remote_name)
        last_error: RegistryError | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                with local_path.open("rb") as stream:
                    response = requests.put(
                        url, data=stream, headers=self._headers(), timeout=self._timeout
                    )
                if response.status_code < 400:
                    logger.info("pushed artifact to %s", url)
                    return url
                last_error = RegistryError(f"push failed: {response.status_code} {response.text}")
                if response.status_code < 500:
                    break
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_error = RegistryError(f"push failed: {exc}")
            if attempt < self._max_attempts:
                self._sleep(attempt)
        raise last_error or RegistryError("push failed")

    def pull(self, remote_name: str, dest: Path) -> Path:
        url = self._url(remote_name)
        last_error: RegistryError | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                with requests.get(
                    url, headers=self._headers(), timeout=self._timeout, stream=True
                ) as response:
                    if response.status_code >= 400:
                        last_error = RegistryError(
                            f"pull failed: {response.status_code} {response.text}"
                        )
                        if response.status_code < 500:
                            break
                        if attempt < self._max_attempts:
                            self._sleep(attempt)
                        continue
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with dest.open("wb") as out:
                        for chunk in response.iter_content(chunk_size=_CHUNK_SIZE):
                            out.write(chunk)
                logger.info("pulled artifact to %s", dest)
                return dest
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_error = RegistryError(f"pull failed: {exc}")
                if attempt < self._max_attempts:
                    self._sleep(attempt)
        raise last_error or RegistryError("pull failed")
