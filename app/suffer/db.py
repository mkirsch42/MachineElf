from datetime import date
from typing import Optional
from psycopg import AsyncConnection

from app.config import get_settings


class SufferStore:
    def __init__(self, guild_id: int, url: Optional[str] = None):
        self._guild = guild_id
        self._url = url or get_settings().db.sql
        self._conn: AsyncConnection | None = None

    async def initialize(self):
        if self._conn is None or self._conn.closed:
            self._conn = await AsyncConnection.connect(self._url, autocommit=True)

    async def __aenter__(self):
        await self.initialize()
        return self

    async def close(self):
        await self._conn.close()
        self._conn = None

    async def __aexit__(self, *_):
        await self.close()

    async def put(
        self,
        *,
        timestamp: Optional[date] = None,
        message: Optional[str] = None,
    ):
        timestamp = timestamp or date.today()
        async with self._conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO suffer
                (guild_id, timestamp, message)
                VALUES (%s, %s, %s)""",
                (self._guild, timestamp, message),
            )

    async def last_n_days(self, n: int) -> int:
        async with self._conn.cursor() as cur:
            return (
                await (
                    await cur.execute(
                        """SELECT COUNT(*)
                        FROM suffer
                        WHERE timestamp >= CURRENT_DATE - %s
                            AND timestamp <= CURRENT_DATE
                            AND guild_id = %s""",
                        (n, self._guild),
                    )
                ).fetchone()
            )[0]

    async def total_count(self) -> int:
        async with self._conn.cursor() as cur:
            return (
                await (
                    await cur.execute(
                        """SELECT COUNT(*)
                        FROM suffer
                        WHERE timestamp <= CURRENT_DATE
                            AND guild_id = %s""",
                        (self._guild,),
                    )
                ).fetchone()
            )[0]
