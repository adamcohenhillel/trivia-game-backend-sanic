from functools import wraps

from sanic.response import json
from jsonschema import validate, draft7_format_checker
import jwt

import settings


def token_required(func):
    """Decorator. Checks if user is logged in - valid JWT"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            token = request.headers['Authorization']
            decoded = jwt.decode(token, settings.SECRET, algorithms='HS256')
            return func(request, decoded, *args, **kwargs)
        except Exception:
            return json({'error': 'unknown token or not provided'}, status=401)
    return wrapper


def validate_json_schema(schema):
    """Decorator. Checks if the request has a valid json data fit to a given schema

    :param schema: python dict in a format of json schema
    :param players: String list with players' usernames
    :return: new wrapped function
    :rtype: function
    :example: how json schema works: https://json-schema.org/
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                validate(request.json,
                        schema=schema,
                        format_checker=draft7_format_checker)
                return func(request, *args, **kwargs)
            except Exception:
                return json({'error': "Bad Arguments"}, status=400)
        return wrapper
    return decorator


def permission_required(permission):
    #TODO: Write decorator for authorized-only endpoints
    pass
