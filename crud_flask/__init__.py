__version__ = "0.1.0"
from flask import Flask
from flask_migrate import Migrate

from .model import configure as config_db
from .serializer import configure as config_ma


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/database.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    config_db(app)
    config_ma(app)

    Migrate(app, app.db)  # type: ignore

    return app
