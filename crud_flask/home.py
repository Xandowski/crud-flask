from flask import Blueprint, render_template

bp_home = Blueprint("home", __name__)


@bp_home.route("/", methods=["GET"])
def home():
    return render_template("index.html")
