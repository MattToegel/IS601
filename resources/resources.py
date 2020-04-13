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

    max = len(res)
    print("Max: " + str(max))
    # TODO land is exploitable because
    # TODO user can sell for free and reacquire if they don't like the resource type
    # TODO fix logic as sometimes(?) resource becomes none
    new_resource = res[randint(1, max)-1]
    print(new_resource)
    if new_resource == Resource.none:
        new_resource = Resource.wood  # temp make it default to wood
    resource.type = new_resource
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