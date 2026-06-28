import json
import logging

import asyncpg

logger = logging.getLogger(__name__)


class PredictionStore:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def record(
        self, model: str, features: list[float], prediction: float, latency_ms: float
    ) -> None:
        await self._pool.execute(
            """
            INSERT INTO predictions (model, features, prediction, latency_ms)
            VALUES ($1, $2, $3, $4)
            """,
            model,
            json.dumps(features),
            prediction,
            latency_ms,
        )

    async def recent_features(self, model: str, limit: int) -> list[list[float]]:
        rows = await self._pool.fetch(
            """
            SELECT features FROM predictions
            WHERE model = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            model,
            limit,
        )
        return [json.loads(row["features"]) for row in rows]
