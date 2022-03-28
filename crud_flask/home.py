from flask import Blueprint, render_template

from .auth import AUTH0_CALLBACK_URL, configure

bp_home = Blueprint("home", __name__)


@bp_home.route("/", methods=["GET"])
def home():
    return render_template("index.html")
