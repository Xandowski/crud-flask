from flask import Blueprint, redirect, session

from .auth import configure

bp_callback = Blueprint("callback", __name__)


@bp_callback.route("/callback", methods=["GET"])
def callback():
    auth0 = configure()
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
