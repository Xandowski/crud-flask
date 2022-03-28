__version__ = "0.1.0"

from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_migrate import Migrate

from . import constants
from .auth import *
from .auth import configure as config_auth
from .callback import bp_callback
from .home import bp_home
from .login import bp_login
from .logout import bp_logout
from .model import configure as config_db
from .serializer import configure as config_ma
from .tasks import bp_tasks


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/database.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.secret_key = constants.SECRET_KEY
    oauth = OAuth(app)
    oauth.register(
        "auth0",
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_DOMAIN,
        access_token_url=f"{AUTH0_DOMAIN}/oauth/token",
        authorize_url=f"{AUTH0_DOMAIN}/authorize",
        client_kwargs={
            "scope": "openid profile email",
        },
    )

    config_db(app)
    config_ma(app)
    config_auth(app)

    Migrate(app, app.db)  # type: ignore

    app.register_blueprint(bp_home)
    app.register_blueprint(bp_login)
    app.register_blueprint(bp_tasks)
    app.register_blueprint(bp_callback)
    app.register_blueprint(bp_logout)

    return app
