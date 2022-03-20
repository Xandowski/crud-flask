import json
from functools import wraps
from os import environ as env

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from six.moves.urllib.parse import urlencode
from werkzeug.exceptions import HTTPException

from . import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)


app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/database.sqlite3"

db = SQLAlchemy(app)

app.secret_key = constants.SECRET_KEY
oauth = OAuth(app)

# TODO https://htmx.org/examples/edit-row/


class Task(db.Model):  # type: ignore
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150))
    create_date = db.Column(db.String(150))

    def __init__(self, name, create_date):
        self.name = name
        self.create_date = create_date


db.create_all()

auth0 = oauth.register(
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


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "profile" not in session:
            # Redirect to Login page here
            return redirect("/")
        return f(*args, **kwargs)

    return decorated


@app.route("/callback")
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()  # type: ignore
    resp = auth0.get("userinfo")  # type: ignore
    userinfo = resp.json()

    # Store the user information in flask session.
    session["jwt_payload"] = userinfo
    session["profile"] = {
        "user_id": userinfo["sub"],
        "name": userinfo["name"],
        "picture": userinfo["picture"],
    }
    return redirect("/profile")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    # return render_template("login.html")
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)  # type: ignore


@app.route("/profile")
@requires_auth
def profile():
    tasks = Task.query.all()
    return render_template(
        "profile.html",
        userinfo=session["profile"],
        userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
        tasks=tasks,
    )


@app.route("/task/create", methods=["POST"])
def create():
    task = Task(request.form["create-task"], request.form["create-date"])
    db.session.add(task)
    db.session.commit()
    response = f"""
    <tr>
        <td><input readonly type="text" name='create-task' value='{task.name}'></td>
         <td><span id='clickableAwesomeFont'><i class='fas fa-edit fa-lg' name='{{name}}' hx-post='/task/edit/{task.id}' hx-target='closest tr' hx-swap='outerHTML swap:0.5s'></i></span><span id='clickableAwesomeFont'><i class='fas fa-trash fa-lg' name='{{name}}' hx-delete='/task/delete/{task.id}' hx-target='closest tr' hx-swap='outerHTML swap:0.5s'></i></span></td>
        <td><input readonly type="date" name='create_date' value='{task.create_date}'></td>
    </tr>
    """
    return response


@app.route("/task/delete/<int:id>", methods=["DELETE"])
def delete(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    print(f"{task.name} removed")
    return ""


@app.route("/task/edit/<int:id>", methods=["GET", "POST"])
def enable_edit(id):
    task = Task.query.get(id)

    response = f"""
    <tr>
        <td><input type="text" value='{task.name}' class="form-control" name='create-task'></td>
         <td><span id='clickableAwesomeFont'><i class='fas fa-square-check fa-lg' name='{{name}}' hx-post='/task/{task.id}/edit' hx-target='closest tr' hx-swap='outerHTML swap:0.5s'></i></span></td>
        <td><input type="date" name='create-date' value='{task.create_date}' class="form-control"></td>
    </tr>
    """
    return response


@app.route("/task/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    task = Task.query.get(id)
    task.name = request.form["create-task"]
    task.create_date = request.form["create-date"]
    db.session.commit()
    response = f"""
    <tr>
        <td><input type="text" value='{task}' class="form-control" name="create-task"></td>
        <td><span id='clickableAwesomeFont'><i class='fas fa-edit fa-lg' name='{{name}}' hx-post='/task/edit/{task.id}' hx-target='closest tr' hx-swap='outerHTML swap:0.5s'></i></span><span id='clickableAwesomeFont'><i class='fas fa-trash fa-lg' name='{{name}}' hx-delete='/task/delete/{task.id}' hx-target='closest tr' hx-swap='outerHTML swap:0.5s'></i></span></td>
        <td><input type="date" name='created_date
        ' value='{task.create_date}' class="form-control" name="create-date"></td>
    </tr>
    """
    print(f"{task.name} edited")
    return response


@app.route("/logout")
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {
        "returnTo": url_for("index", _external=True),
        "client_id": AUTH0_CLIENT_ID,
    }
    return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))  # type: ignore


if __name__ == "__main__":
    app.run(debug=True)
