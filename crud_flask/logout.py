from flask import Blueprint, render_template, session, url_for

from .auth import AUTH0_CLIENT_ID, configure

bp_logout = Blueprint("logout", __name__)


@bp_logout.route("/logout", methods=["GET"])
def logout():
    auth0 = configure()
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {
        "returnTo": url_for("index", _external=True),
        "client_id": AUTH0_CLIENT_ID,
    }
    return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))  # type: ignore
