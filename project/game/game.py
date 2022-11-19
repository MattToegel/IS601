from flask import Blueprint, render_template, flash, redirect, url_for, current_app, session
from game.forms import GameForm
from sql.db import DB

from flask_login import login_user, login_required, logout_user, current_user
from auth.models import User
from flask_bcrypt import Bcrypt
game = Blueprint('game', __name__, url_prefix='/',template_folder='templates')

@game.route("/game", methods=["GET"])
@login_required
def play():
    form = GameForm()
    return render_template("game.html", form=form)

@game.route("/save", methods=["POST"])
def save():
    form = GameForm()
    if form.validate_on_submit():
        user_id = current_user.get_id()
        score = form.score.data
        # TODO save
        print(f"score {score}")
        flash("Saved score", "success")
    return redirect(url_for('game.play'))