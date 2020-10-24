import asyncio
from sanic import Sanic

import settings
from core import listeners
from apps.auth.views import auth_bp
from apps.game.views import game_bp


app = Sanic(__name__)


# Listeners
app.register_listener(listeners.initial, "before_server_start")
app.register_listener(listeners.final, "before_server_stop")


# Blueprints
app.blueprint(auth_bp, url_prefix='/auth')
app.blueprint(game_bp, url_prefix='/game')


if __name__ == '__main__':
    app.run(host="0.0.0.0",
            port=settings.PORT,
            workers=settings.WORKERS,
            debug=settings.DEBUG,
            access_log=settings.ACCESS_LOG)
