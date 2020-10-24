import asyncio
import requests


IP_PORT = "127.0.0.1:5000"
LOGIN_URL = "http://" + IP_PORT + "/auth/login"
REGISTER_URL = IP_PORT + "/api/register"
WEBSOCKET_URL = "ws://" + IP_PORT + "/game/random"


async def get_login_access(username, password):
    """Try to login and get accerss token"""
    try:
        response = requests.post(LOGIN_URL, json={"username": username,
                                                  "password": password}).json()
        return response["token"]
    except:
        return None
