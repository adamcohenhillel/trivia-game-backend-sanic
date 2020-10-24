import asyncio
from tortoise import Tortoise
import aioredis
import json

import settings
from apps.game.matchmaker import fifo_matchmaker


async def initial(app, loop):
    """Initial DB connection and redis pool.

    :param app: Sanic app object
    :param loop: The event loop
    """
    app.redis_pool = await aioredis.create_redis_pool(settings.REDIS_ADDR)
    await app.redis_pool.execute("flushdb")
    
    await Tortoise.init(db_url=settings.DATABASE,
                        modules={'models': ['apps.auth.models']})
    await Tortoise.generate_schemas()
    # Run the match maker corutine
    app.add_task(fifo_matchmaker(app.redis_pool))


async def final(app, loop):
    """Close database connection and redis pool before exit.

    :param app: Sanic app object
    :param loop: The asyncio event loop
    """
    app.redis_pool.close()
    await app.redis_pool.wait_closed()
    await Tortoise.close_connections()
