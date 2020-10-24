import asyncio
import websockets
import json
import random
import requests

import consts


async def register_new_user(username, password):
    """Try to register and get accerss token"""
    email = f"{username}@gmail.com"

    try:
        response = requests.post(consts.REGISTER_URL, json={"username": username,
                                                            "password": password,
                                                            "password_confirmation": password,
                                                            "email": email}).json()
        print("You registered! run again and play!")
    except Exception:
        print("Can't register user")


async def get_access_token(username, password):
    """Try to login and get accerss token"""
    try:
        response = requests.post(consts.LOGIN_URL, json={"username": username,
                                                        "password": password}).json()
        return response["token"]
    except:
        return None


async def play(username, password, debug=True):
    """Note: this client is for testing only. it's not fully async and not error-safe
    """
    access_token = await get_access_token(username, password)

    if access_token:
        authorize_header = {"Authorization": access_token}
        async with websockets.connect(consts.WEBSOCKET_URL,
                                      extra_headers=authorize_header) as websocket:
            
            print("Waiting for match...") and debug

            game_details = json.loads(await websocket.recv())
            
            print("Match found, game start..") and debug

            question = 0
            while question < 10:
                question_data = game_details["questions"][question]
                print(f"**** {question+1}/10 ****") and debug
                print(f"{question}) {question_data['question']}:")
                print(f"A: {question_data['A']}")
                print(f"B: {question_data['B']}")
                print(f"C: {question_data['C']}")

                user_answer = input("Answer > ")
                while user_answer not in ["A", "B", "C"]:
                    print("You must choose between A, B and C!")
                    user_answer = input("Answer (A/B/C) > ")

                score = 0
                if user_answer == question_data["correct"]:
                    score = 1000

                await websocket.send(json.dumps({"type": "update", "score": score}))

                print("Waiting for the other player...") and debug
                wait_for_competitor = True
                while wait_for_competitor:
                    await websocket.send(json.dumps({"type": "check"}))
                    data = json.loads(await websocket.recv())

                    if data["type"] == "user_exit":
                        print("The other player exit, game ending")
                        question = 500
                        break
                    elif data["type"] == "update":
                        if data["players"][0]["state"] == data["players"][1]["state"]:
                            wait_for_competitor = False
                            break
                    await asyncio.sleep(1)
                question = question + 1
            
            #Game ends:
            await websocket.send(json.dumps({"type": "check"}))
            data = json.loads(await websocket.recv())   
            print("GAME ENDED: ", data)
            await websocket.close()

    else:
        print("Unable to authorize") and debug


def main():
    loop = asyncio.get_event_loop()

    command = input("What you want to do? (register / play) > ")
    while command not in ["register", "play"]:
        command = input("Command must be register OR play > ")
    
    if command == "register":
        name = input("username >")
        password = input("password >")
        r_password = input("repeat password >")
        while r_password != password:
            print("Passwords not match! Try again:")
            password = input("password >")
            r_password = input("repeat password >")
        loop.run_until_complete(register_new_user(name, password))
        
    else:
        username = input("username >")
        password = input("password >")
        loop.run_until_complete(play(username, password))


if __name__ == "__main__":
    main()