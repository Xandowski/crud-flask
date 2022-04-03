from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import auto_field

from .model import Task, User

ma = Marshmallow()


def configure(app):
    ma.init_app(app)


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        include_fk = True
        load_instance = True


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
