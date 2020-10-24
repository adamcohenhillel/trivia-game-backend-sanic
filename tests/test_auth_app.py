from datetime import datetime

import asyncio
import pytest
import json

from main import app


def test_register_and_delete():
    unique_username = "testuser_{}".format(datetime.now().strftime("%d%H%M%S"))
    send = {"username": unique_username,
            "password": "12345678",
            "password_confirmation": "12345678",
            "email": f"{unique_username}@gmail.com"}

    _, response = app.test_client.post("/auth/register", json=send)
    assert response.status == 200
    assert "token" in response.json

    auth_header = {"Authorization": response.json.get("token")}
    _, response = app.test_client.delete(f"/auth/user/{unique_username}",
                                                headers=auth_header)
    assert response.status == 200


def test_register_existing_username():
    send = {"username": "adam",
            "password": "12345678",
            "password_confirmation": "12345678",
            "email": "adam@gmail.com"}

    _, response = app.test_client.post("/auth/register", json=send)
    assert response.status == 400
    assert "error" in response.json


def test_register_bad_scheme():
    send = {"not_username": "adam",
            "password": "12345678",
            "password_confirmation": "12345678",
            "email": "adam@gmail.com"}

    _, response = app.test_client.post("/auth/register", json=send)
    assert response.status == 400
    assert "error" in response.json


def test_login_good():
    send = {"username": "adam", "password": "12345678"}
    _, response = app.test_client.post("/auth/login", json=send)

    assert response.status == 200
    assert "token" in response.json


def test_login_bad_credentials():
    send = {"username": "adam", "password": "wrongpass"}
    _, response = app.test_client.post("/auth/login", json=send)

    assert response.status == 400
    assert "error" in response.json


def test_login_bad_scheme():
    send = {"notusername": "adam", "password": "12345678"}
    _, response = app.test_client.post("/auth/login", json=send)

    assert response.status == 400
    assert "error" in response.json


def test_leaderboard_with_token():
    send = {"username": "adam", "password": "12345678"}
    _, response = app.test_client.post("/auth/login", json=send)
    token = response.json.get("token")
    
    authorize_header = {"Authorization": token}
    _, response = app.test_client.get("/auth/leaderboard", headers=authorize_header)
    assert response.status == 200
    assert len(response.json.get("users")) < 100


def test_leaderboard_with_token():
    send = {"username": "adam", "password": "12345678"}
    _, response = app.test_client.post("/auth/login", json=send)
    token = response.json.get("token")
    
    authorize_header = {"Authorization": token}
    _, response = app.test_client.get("/auth/leaderboard", headers=authorize_header)
    assert response.status == 200
    assert len(response.json.get("users")) < 100


def test_leaderboard_no_token():
    _, response = app.test_client.get("/auth/leaderboard")
    assert response.status == 401
    assert "error" in response.json


def test_leaderboard_bad_token():
    authorize_header = {"Authorization": "STAMTOKENNOTGOOD"}
    _, response = app.test_client.get("/auth/leaderboard", headers=authorize_header)
    assert response.status == 401
    assert "error" in response.json


def test_user_update_win():
    send = {"username": "adam", "password": "12345678"}
    _, response = app.test_client.post("/auth/login", json=send)
    token = response.json.get("token")
    
    authorize_header = {"Authorization": token}
    _, response = app.test_client.put("/auth/user/adam", headers=authorize_header)
    assert response.status == 200
    assert "msg" in response.json


def test_user_update_win_token_not_match_username():
    send = {"username": "adam", "password": "12345678"}
    _, response = app.test_client.post("/auth/login", json=send)
    token = response.json.get("token")
    
    authorize_header = {"Authorization": token}
    _, response = app.test_client.put("/auth/user/notadam", headers=authorize_header)
    assert response.status == 503
    assert "error" in response.json


def test_user_update_win_bad_token():
    authorize_header = {"Authorization": "this_is_bad_token"}
    _, response = app.test_client.put("/auth/user/adam", headers=authorize_header)
    assert response.status == 401
    assert "error" in response.json

