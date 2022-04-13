from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db


class Task(db.Model):  # type: ignore
    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    create_date = db.Column(db.String(150))
    user = db.relationship('User', backref='task', lazy=True)

    def __init__(self, user_id, name, create_date):
        self.user_id = user_id
        self.name = name
        self.create_date = create_date


class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    nickname = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    
    def __init__(self, username, lastname, nickname, email):
        self.username = username
        self.lastname = lastname
        self.nickname = nickname
        self.email = email
