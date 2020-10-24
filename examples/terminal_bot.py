import asyncio
import websockets
import json
import random

import consts
from examples.basic_interact import get_access_token


async def nested_terminal_bot(name, password, debug=True):
    access_token = await get_access_token(name, password)

    if access_token:
        authorize_header = {"Authorization": access_token}
        async with websockets.connect(consts.WEBSOCKET_URL,
                                      extra_headers=authorize_header) as websocket:
            
            game_details = json.loads(await websocket.recv())
            print("Match found, game start..") and debug

            question = 0
            while question < 10:
                question_data = game_details["questions"][question]

                thinking_time = random.random() # How much time the bot will "think"
                print(f"question: {question}, thinking: {thinking_time*10} sec..") and debug
                await asyncio.sleep(thinking_time*10)

                answer = random.choice(["A", "B", "C"])
                score = 0
                if answer == question_data["correct"]:
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
    print("Bot must be logged in:")
    name = input("username >")
    password = input("password >")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(nested_terminal_bot(name, password))


if __name__ == "__main__":
    main()