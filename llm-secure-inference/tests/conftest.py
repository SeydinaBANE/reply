from redis.exceptions import RedisError


class FakeRedis:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}

    async def eval(self, script: str, numkeys: int, *keys_and_args: object) -> int:
        key = str(keys_and_args[0])
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def ping(self) -> bool:
        return True


class FailingRedis:
    async def eval(self, script: str, numkeys: int, *keys_and_args: object) -> int:
        raise RedisError("connection refused")

    async def ping(self) -> bool:
        raise RedisError("connection refused")
