from random import seed, randint

from flask import Blueprint

from resources.models import ResourceNode, ResourceType, OreType

resources_bp = Blueprint('resources', __name__, template_folder='templates')


def acquire_new_resource():
    resource = ResourceNode()
    seed()
    resource.available = randint(10, 50)
    resource.maximum = resource.available
    resource.type = ResourceType(randint(1, 2))
    if resource.type == ResourceType.ore:
        resource.sub_type = OreType(randint(1, 3))
    else:
        resource.sub_type = OreType.none
    # resource.land_id = land_id
    return resource


def harvest(resource_id, worker):
    resource = ResourceNode.query.get(int(resource_id))
    n = 0
    if resource.available > 0:
        n = resource.harvest(worker)
    return n