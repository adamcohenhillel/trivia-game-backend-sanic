from sanic import Blueprint
from sanic.response import json
import jwt

from core.decorators import validate_json_schema, token_required
from .models import User
from .utils import hash_password, validate_schemes
from settings import SECRET


auth_bp = Blueprint("auth_bp")


@auth_bp.route("/register", methods=["POST"])
@validate_json_schema(validate_schemes["REGISTER"])
async def register(request):
    """Register a new user and generate JWT
    
    :return: json information with keys token/error
    :rtype: Json
    """
    try:
        if request.json.get("password") != request.json.get("password_confirmation"):
            raise ValueError
        else:
            user = await User.create(
                username=request.json.get("username"),
                password=hash_password(request.json.get("password"), SECRET),
                email=request.json.get("email"))

            return json({'token': jwt.encode({"username": user.username},
                                              SECRET,
                                              algorithm='HS256').decode('utf-8')})
    except Exception as e:
        print(e.args)
        return json({'error': "Bad Arguments"}, status=400)


@auth_bp.route("/login", methods=["POST"])
@validate_json_schema(validate_schemes["LOGIN"])
async def login(request):
    """Login user (generate JWT)
    
    :return: json information with keys token/error
    :rtype: Json
    """
    try:
        user = await User.get(username=request.json.get("username"))
        if user and user.password == hash_password(request.json.get("password"), SECRET):
            return json({'token': jwt.encode({"username": user.username},
                                              SECRET,
                                              algorithm='HS256').decode('utf-8')})
        else:
            raise ValueError
    except Exception:
        return json({'error': "Bad Arguments"}, status=400)


@auth_bp.route("/user/<name:string>", methods=["PUT", "DELETE"])
@token_required
async def user(request, payload, name):
    """User endpoints: PUT wins or DELETE self from db (for testing)

    :param request: Sanic http Request
    :param payload: Information from JWT (dict)
    :return: information based on request type: get = details
    :rtype: Json
    """
    try:
        if name == payload["username"]:
            user = await User.get(username=name)
            if request.method == "DELETE":
                await User.filter(id=user.id).delete()
            elif request.method == "PUT":
                await User.filter(id=user.id).update(wins=user.wins + 1)
            return json({"msg": "done"})
        else:
            raise Exception

    except Exception:
        return json({"error": "Not Available"}, status=503)


@auth_bp.route("/leaderboard", methods=["GET"])
@token_required
async def leaderboard(request, payload):
    """Return the top 100 users in the game, based on number of wins

    :param request: Sanic http Request
    :param payload: Information from JWT
    :return: json information
    :rtype: Json
    """
    try:
        top = await User.all().order_by("-wins").limit(100)
        return json({"users": [{u.username: u.wins} for u in top]})
    except Exception:
        return json({"error": "Not Available"}, status=503)
