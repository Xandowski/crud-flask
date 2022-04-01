from flask_marshmallow import Marshmallow, fields

from .model import Task, User

ma = Marshmallow()


def configure(app):
    ma.init_app(app)


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    username = fields.Str(required=True)
