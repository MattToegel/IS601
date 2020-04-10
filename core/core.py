from flask import Blueprint, render_template
from flask_login import login_required, current_user

core_bp = Blueprint('core', __name__, template_folder='templates')


class CachedStaticProperty:  # https://stackoverflow.com/questions/39498891/computed-static-property-in-python
    """Works like @property and @staticmethod combined"""

    def __init__(self, func):
        self.func = func

    def __get__(self, inst, owner):
        result = self.func()
        setattr(owner, self.func.__name__, result)
        return result


@core_bp.route('/')
def index():
    return render_template('index.html')


@core_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)
