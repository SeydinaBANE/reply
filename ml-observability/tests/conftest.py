import json


class FakePool:
    def __init__(self, rows: list[dict[str, str]] | None = None) -> None:
        self.rows = rows if rows is not None else []
        self.executed: list[tuple[object, ...]] = []

    async def execute(self, query: str, *args: object) -> None:
        self.executed.append(args)

    async def fetch(self, query: str, *args: object) -> list[dict[str, str]]:
        return self.rows

    async def fetchval(self, query: str, *args: object) -> int:
        return 1


class FakeRedis:
    def __init__(self) -> None:
        self.published: list[tuple[str, str]] = []

    async def publish(self, channel: str, message: str) -> None:
        self.published.append((channel, message))


def feature_rows(vectors: list[list[float]]) -> list[dict[str, str]]:
    return [{"features": json.dumps(vector)} for vector in vectors]
