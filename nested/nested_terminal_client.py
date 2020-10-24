import asyncio
import websockets
import json
import random

import utils


async def nested_terminal_client(name, password, debug=True):
    """Note: this client is for testing only. it's not fully async and not error-safe
    """
    access_token = await utils.get_login_access(name, password)

    if access_token:
        authorize_header = {"Authorization": access_token}
        async with websockets.connect(utils.WEBSOCKET_URL,
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
    print("Please login:")
    name = input("name >")
    password = input("password >")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(nested_terminal_client(name, password))


if __name__ == "__main__":
    main()