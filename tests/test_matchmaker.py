import pytest
import asyncio
import aioredis

from apps.game import matchmaker
from apps.game import constants


async def test_new_redis_room(redis_pool):
    players = ["adam", "haran"]
    room = await matchmaker._new_redis_room(redis_pool, players)
    assert "channel" in room
    assert "questions" in room
    assert "players" in room
    assert len(room["questions"]) ==  10
    assert len(room["players"]) ==  2

    game_state = await redis_pool.hgetall(room["channel"])
    assert game_state is not None

    redis_pool.close()
    await redis_pool.wait_closed()


async def test_notify_players(redis_pool):
    name = "adam"
    with await redis_pool as conn:
        sub = (await conn.subscribe(name))[0]
        room = await matchmaker._new_redis_room(redis_pool, [name])
        await matchmaker._notify_players(redis_pool, room)
        game_details = await sub.get_json()
        assert game_details != None
        assert game_details["type"] == "start"
        await conn.unsubscribe("")

    redis_pool.close()
    await redis_pool.wait_closed()


async def test_if_players_online_good(redis_pool):
    players = ["adam", "haran"]
    subs = []
    for p in players:
        (await redis_pool.subscribe(p))[0]
    
    answer = await matchmaker._is_players_online(redis_pool, players)
    assert answer
    
    await redis_pool.unsubscribe("")
    redis_pool.close()
    await redis_pool.wait_closed()


async def test_if_players_online_bad(redis_pool):
    players = ["adam", "haran"]
    players_full = players + ["daniel"]
    subs = []
    for p in players:
        (await redis_pool.subscribe(p))[0]
    
    answer = await matchmaker._is_players_online(redis_pool, players_full)
    assert not answer
    
    await redis_pool.unsubscribe("")
    redis_pool.close()
    await redis_pool.wait_closed()


async def test_matchmaker(redis_pool):
    players = ["adam", "haran"]
    subs = []
    for p in players:
        subs.append((await redis_pool.subscribe(p))[0])
        await redis_pool.lpush(constants.MATCH_QUEUE, p)
    
    matchmaker_task = asyncio.create_task(matchmaker.fifo_matchmaker(redis_pool))

    for sub in subs:
        game_details = await sub.get_json()
        assert game_details != None
        assert game_details["type"] == "start"
    
    matchmaker_task.cancel()
    await redis_pool.unsubscribe("")
    redis_pool.close()
    await redis_pool.wait_closed()
