from random import seed, randint

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from resources.models import ResourceNode, Resource

resources_bp = Blueprint('resources', __name__, template_folder='templates')


def acquire_new_resource():
    resource = ResourceNode()
    seed()
    resource.available = randint(10, 50)
    resource.maximum = resource.available
    res = []
    for r in Resource:
        if r.is_harvestable():
            res.append(r)
    resource.type = res[randint(1, 2)]
    return resource


def harvest(resource_id, worker):
    resource = ResourceNode.query.get(int(resource_id))
    n = 0
    if resource.available > 0:
        n = resource.harvest(worker)
    # updated to return resource too
    return [resource, n]


@resources_bp.route('/inventory')
@login_required
def my_inventory():
    inventory = current_user.inventory
    return render_template("inventory.html", inventory=inventory, title="My Inventory")