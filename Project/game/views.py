from flask import Blueprint, request, render_template

game = Blueprint('game', __name__,template_folder='templates', url_prefix='/')


@game.route('/game')
def index():
    return render_template("game.html")
