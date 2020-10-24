import asyncio
import pytest
import aioredis
from sanic.websocket import WebSocketProtocol

import settings
from main import app


@pytest.fixture
def test_cli(loop, sanic_client):
    return loop.run_until_complete(sanic_client(app, protocol=WebSocketProtocol))


@pytest.fixture
async def redis_pool():
    redis_pool = await aioredis.create_redis_pool(settings.REDIS_ADDR)
    await redis_pool.execute("flushdb")
    return redis_pool
