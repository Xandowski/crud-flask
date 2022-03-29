__version__ = "0.1.0"


from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_migrate import Migrate

from . import constants
from .auth import bp_auth
from .auth import configure as config_auth
from .home import bp_home
from .model import configure as config_db
from .serializer import configure as config_ma
from .tasks import bp_tasks


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/database.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.secret_key = constants.SECRET_KEY

    config_db(app)
    config_ma(app)
    config_auth(app)

    Migrate(app, app.db)  # type: ignore

    app.register_blueprint(bp_home)
    app.register_blueprint(bp_tasks)
    app.register_blueprint(bp_auth)

    return app
