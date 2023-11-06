from flask import Blueprint, render_template
home = Blueprint('home', __name__, url_prefix='/')

# TODO DO NOT EDIT
@home.route('/')
def index():
    return render_template("index.html")