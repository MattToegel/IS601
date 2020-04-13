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
@core_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id=-1):
    if user_id == -1:
        user = current_user
    else:
        from auth.models import User
        user = User.query.get(int(user_id))
    if user is None:
        pass
    else:
        from resources.models import InventoryToResource
        lots = len(user.land)
        workers = len(user.workers)
        wood = user.inventory.resources.filter('wood' in InventoryToResource.type.name).all()
        print(wood)
        ore = user.inventory.resources.filter('ore' in InventoryToResource.type.name).all()
        ingot = user.inventory.resources.filter('ingot' in InventoryToResource.type.name).all()
    return render_template('profile.html', name=user.name,coins=user.get_coins(), num_lots=lots, num_workers=workers,
                           wood_types=wood, ore_types=ore, ingot_types=ingot)
