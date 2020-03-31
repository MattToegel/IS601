from flask import Blueprint, render_template
from flask_login import login_required, current_user

core_bp = Blueprint('core', __name__, template_folder='templates')


@core_bp.route('/')
def index():
    return render_template('index.html')


@core_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)
