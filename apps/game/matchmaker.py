import asyncio
from asyncio.exceptions import CancelledError
import aioredis
import random
import json

import settings
from .constants import MessageType, MATCH_QUEUE


_QUESTIONS = None


async def _new_redis_room(r_conn, players):
    """Create new room instance in redis memory.

    :param r_conn: RedisConnection object to quest redis database
    :param players: list of players (str, usernames) to create the room for
    :return: the room details: new channel name, 10 questions, players in the room
    :rtype: dict
    """
    global _QUESTIONS

    room_name = "-".join(players)
    questions_generate = random.sample(_QUESTIONS, k=10)
    
    game = {}
    for p in players:
        game[p + "_score"] = 0
        game[p + "_state"] = 0
    await r_conn.hmset_dict(room_name, game)
    await r_conn.expire(room_name, 500)

    game = {
        "channel": room_name,
        "questions":questions_generate,
        "players": players,
    }

    return game


async def _notify_players(r_conn, room_details):
    """Notify the players that a game start in a new redis channel.
    we do that by publish the game details to the player unique redis channel (his name)

    :param r_conn: RedisConnection object to quest redis database
    :param room_details: Dict with room information
    """
    room_details["type"] = MessageType.GAME_START
    room_details["source"] = None
    for player_username in room_details["players"]:
        await r_conn.publish_json(player_username, room_details)


async def _is_players_online(r_conn, players):
    """Check if players still connected to the server
    by verify that they still subscribe to thier own redis channel.

    :param r_conn: RedisConnection object to quest redis database
    :param players: String list with players' usernames
    :return: True if everyone still subscribed, False otherwise.
    :rtype: bool
    """
    players_channels = await r_conn.pubsub_numsub(*players)
    for channel, subscribers in players_channels.items():
        if subscribers == 0:
            players.remove(channel.decode())
            return False
    return True


async def _load_questions():
    """Load questions to global var from json file"""
    global _QUESTIONS
    with open(settings.QUESTIONS_FILE, "r") as qf:
        _QUESTIONS = json.load(qf)


async def fifo_matchmaker(redis_pool):
    """Infinity loop to match two websockets together in a unique redis channel
    using redis list as a queue -> FIFO and SUB functionality

    :flow:  1) Block and wait until popup username from MATCH_QUEUE
            2) Save the username in the waiting list
            3) Go back to (1) until waiting list has 2 players
            4) check if the players still connected (by checking they still subscribed 
                to their own redis channel)
            5) Create a new game instance in the redis memory
                and send the players the details
            6) Matchmaker done his job - Going back to (1)


    :param redis_pool: The server global redis pool
    """
    await _load_questions()
    players_for_match = []

    while True:
        try:
            if not redis_pool:
                raise CancelledError
            else:
                pop = await redis_pool.brpop(MATCH_QUEUE, 0)
                player = pop[1].decode()
                if player not in players_for_match:
                    players_for_match.append(player)

                if len(players_for_match) == 2 and \
                    await _is_players_online(redis_pool, players_for_match):

                    redis_room = await _new_redis_room(redis_pool, players_for_match)
                    await _notify_players(redis_pool, redis_room)
                    players_for_match = []

        except CancelledError:
            break
