import asyncio
from asyncio.exceptions import CancelledError
import aioredis
from sanic import Blueprint
from websockets.exceptions import WebSocketException
from sanic.log import logger
import json

from core.decorators import token_required
from .pubsub import ws_publisher, ws_subscriber
from .constants import MessageType, MATCH_QUEUE
import settings
import sys


game_bp = Blueprint("game_bp")


@game_bp.websocket('/random')
@token_required
async def random_ws_handler(request, payload, ws):
    """Websocket handler for fifo match making.
    When called, insert username to match queue,
    subscribe to unique redis channel (username)
    and wait until data reciceve from that channel.
    When data is receiving, it will be game game details
    or game cancelled. With game details we can now start
    publish and subscribe loop for the new game - and they 
    will handle the game flow.

    :param request: HTTP request details
    :param payload: user data from JWT
    :param ws: the websocket
    """
    username = payload["username"]
    redis_sub = None
    redis_pub = None
    game_details = None
    try:
        redis_sub = await aioredis.create_redis(settings.REDIS_ADDR)
        redis_pub = await aioredis.create_redis(settings.REDIS_ADDR)

        # Subscrie to user's dedicated redis channel(user's username)
        # Push itself to the qaiting queue
        # wait for response from the channel with game details
        subscribe_channel = (await redis_sub.subscribe(username))[0]
        await redis_pub.lpush(MATCH_QUEUE, username)
        
        game_details = await subscribe_channel.get_json()
        if game_details:
            await ws.send(json.dumps(game_details))

            # Start publish and subscribe coroutines
            # to handle incoming messages from the websocket
            # and outcoming messages from the channel to the WS (frontend)
            await asyncio.gather(ws_publisher(ws,
                                              redis_pub,
                                              game_details["channel"],
                                              username),
                                ws_subscriber(ws,
                                              redis_sub,
                                              game_details["channel"],
                                              username),
                                return_exceptions=False)
        else:
            await ws.send(json.dumps({"type": MessageType.GAME_CANCELLED}))

    except (Exception, CancelledError) as e:
        logger.debug("WEBSOCKET DISCONNECTED")

    finally:
        if ws:
            await ws.close()

        if game_details:
            await redis_pub.publish(game_details["channel"],
                                    json.dumps({"type": MessageType.USER_EXIT}))
        else:
            await redis_pub.lrem(MATCH_QUEUE, 1, username)

        await redis_sub.unsubscribe("")
        redis_sub.close()   # close without await
        redis_pub.close()
