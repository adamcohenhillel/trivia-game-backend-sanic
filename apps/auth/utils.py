import hashlib


def hash_password(password, salt):
    salted = password + salt
    return hashlib.sha512(salted.encode("utf8")).hexdigest()


validate_schemes = {
    "REGISTER": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "format": "email"},
            "username": {"type": "string"},
            "password": {"type": "string"},
            "password_confirmation": {"type": "string"}
        },
    },
    "LOGIN": {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"},
        },
    }
}
