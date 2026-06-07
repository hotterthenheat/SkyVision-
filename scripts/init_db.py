import asyncio

from skyvision.db import models  # noqa: F401
from skyvision.db.base import Base
from skyvision.db.session import engine


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(main())
