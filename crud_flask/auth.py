from functools import wraps
from os import environ as env
from urllib.parse import urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Blueprint, redirect, session, url_for

bp_auth = Blueprint("auth", __name__)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get("AUTH0_CALLBACK_URL")
AUTH0_CLIENT_ID = env.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = env.get("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = env.get("AUTH0_DOMAIN")
AUTH0_AUDIENCE = env.get("AUTH0_AUDIENCE")


def configure(app):
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

    @bp_auth.route("/login", methods=["GET"])
    def login():
        # return render_template("login.html")
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)

    @bp_auth.route("/logout", methods=["GET"])
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {
            "returnTo": url_for("home.home", _external=True),
            "client_id": AUTH0_CLIENT_ID,
        }
        return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))

    @bp_auth.route("/callback", methods=["GET"])
    def callback():
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


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "profile" not in session:
            # Redirect to Login page here
            return redirect("/")
        return f(*args, **kwargs)

    return decorated


# type: ignore
