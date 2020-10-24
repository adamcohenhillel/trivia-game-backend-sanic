import asyncio
import aioredis
import json

from .constants import MessageType


async def _get_game_state(redis_conn, game_channel):
    """Fetch the game details from the redis memory.
    game state saved in redis memory as hash, decoding proccess is needed/

    :param redis: The connection to the redis server
    :param game_channel: Game name to find the instance in redis memory
    :return: game state (players, scores, states)
    :rtype: dict
    """
    hash_game_state = await redis_conn.hgetall(game_channel)
    game_data = {}
    game_data["players"] = []

    # Run in loop to make the game `redis hash` in python dict structure
    for k, v in hash_game_state.items():
        nck, v_type = k.decode().split("_") #example: k = adam_score -> nck=adam, v_type=score
        v = v.decode()
        exists = False
        for player in game_data["players"]:
            if nck == player["username"]:
                player[v_type] = v
                exists = True
        if not exists:
            game_data["players"].append({"username": nck, v_type: v})

    return game_data


async def _update_game_state(redis_conn, game_channel, data):
    """Update user score and state in the redis room instance.

    :param redis: The connection to the redis server
    :param game_channel: Game name to find the instance in redis memory
    :param data: the data got from the user (score i)
    """
    await redis_conn.hincrby(game_channel, data["source"] + "_score", data["score"])
    await redis_conn.hincrby(game_channel, data["source"] + "_state", 1)


async def ws_subscriber(ws, redis_conn, game_channel, username):
    """Subscriber coroutine who waits for data from redis channel
    and pass it towards the client through the given websocket.

    > Recv from redis channel
    < Pass to websocket
    
    :param ws: websocket connection
    :param r_conn: redis connection
    :param game_channel: game room name, str
    :param username: websocket client username
    """
    recv_channel = (await redis_conn.subscribe(game_channel))[0]
    while await recv_channel.wait_message():
        data = await recv_channel.get_json()
        if data["source"] != username:
            await ws.send(json.dumps(data))


async def ws_publisher(ws, redis_conn, game_channel, username):
    """Publisher coroutine who waits for data from websocket
    and send it out to the whole given redis channel
    
    > Recv from Websocker
    < Pass to redis channel
    
    :param ws: websocket connection
    :param r_conn: redis connection
    :param game_channel: game room name, str
    :param username: websocket client username
    """
    while True:
        data = json.loads(await ws.recv())
        data["source"] = username

        if data["type"] == MessageType.GAME_UPDATE:
            await _update_game_state(redis_conn, game_channel, data)

        elif data["type"] == MessageType.GAME_CHECK:
            state = await _get_game_state(redis_conn, game_channel)
            state["type"] = MessageType.GAME_UPDATE
            await ws.send(json.dumps(state))

        elif data["type"] == MessageType.EMOJI:
            await redis_conn.publish_json(game_channel, data)

