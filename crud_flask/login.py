from authlib.integrations.flask_client import OAuth
from flask import Blueprint

from .auth import AUTH0_CALLBACK_URL, configure

bp_login = Blueprint("login", __name__)


@bp_login.route("/login", methods=["GET"])
def login():
    auth0 = configure()
    # return render_template("login.html")
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)
