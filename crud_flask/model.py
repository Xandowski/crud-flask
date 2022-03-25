from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db


class Task(db.Model):  # type: ignore
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150))
    create_date = db.Column(db.String(150))

    def __init__(self, name, create_date):
        self.name = name
        self.create_date = create_date
