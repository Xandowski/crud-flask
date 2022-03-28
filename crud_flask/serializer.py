from flask_marshmallow import Marshmallow

from .model import Task

ma = Marshmallow()


def configure(app):
    ma.init_app(app)


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
