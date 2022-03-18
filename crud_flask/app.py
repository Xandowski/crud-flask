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
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/tasks"
db = SQLAlchemy(app)
app.secret_key = constants.SECRET_KEY
oauth = OAuth(app)

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
    return render_template(
        "profile.html",
        userinfo=session["profile"],
        userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
    )


@app.route("/task/create", methods=["POST"])
def create():
    task = request.form["create-task"]
    date = request.form["create-date"]
    vals = json.dumps({"delete": task})
    vals2 = json.dumps({"edit": task})
    response = f"""
    <tr>
        <td><input readonly type="text" name='{task}' value='{task}'></td>
         <td><span id='clickableAwesomeFont'><i class='fas fa-edit fa-lg' name='{{name}}' hx-post='/task/edit' hx-vals='{vals2}' hx-target='closest tr' hx-swap='outerHTML swap:0.5s'></i></span><span id='clickableAwesomeFont'><i class='fas fa-trash fa-lg' name='{{name}}' hx-post='/task/delete' hx-vals='{vals}' hx-target='closest tr' hx-swap='outerHTML swap:0.5s'></i></span></td>
        <td><input readonly type="date" name='{date}' value='{date}'></td>
    </tr>
    """
    return response


@app.route("/task/delete", methods=["POST"])
def delete():
    name = request.form["delete"]
    print(f"{name} removed")
    return ""


@app.route("/task/edit", methods=["POST"])
def edit():
    task = request.form["edit"]
    date = request.form["edit"]
    vals = json.dumps({"edit": task})
    response = f"""
    <tr>
        <td><input type="text" name='{task}' value='{task}' class="form-control" name="create-task"></td>
        
         <td><span id='clickableAwesomeFont'><i class='fas fa-square-check fa-lg' name='{{name}}' hx-post='/task/create' hx-vals='{vals}' hx-target='closest tr' hx-swap='outerHTML swap:0.5s'></i></span></td>
        <td><input type="date" name='{date}' value='{date}' class="form-control" name="create-date"></td>
    </tr>
    """
    print(f"{task} edited")
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
