import asyncio
import pytest
import json

from main import app
from apps.game import matchmaker
from apps.game import constants


async def test_websocket_start_game_success(test_cli, redis_pool):
    # Push to queue nested player (without auth)
    matchmaker_task = asyncio.create_task(matchmaker.fifo_matchmaker(redis_pool))

    nested_player = "some_name"
    nested_sub = (await redis_pool.subscribe(nested_player))[0]
    await redis_pool.lpush(constants.MATCH_QUEUE, nested_player)

    real_user = {"username": "adam", "password": "12345678"}
    response = await test_cli.post("/auth/login", json=real_user)
    token = (await response.json())["token"]
    auth_header = {"Authorization": token}
    ws = await test_cli.ws_connect("/game/random", headers=auth_header)
    msg = await ws.receive()

    game_details = json.loads(msg.data)
    assert game_details != None
    assert game_details["type"] == "start"
    
    matchmaker_task.cancel()
    await redis_pool.unsubscribe("")
    redis_pool.close()
    await redis_pool.wait_closed()
    await ws.close()
