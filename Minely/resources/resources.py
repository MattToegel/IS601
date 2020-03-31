from random import seed, randint

from flask import Blueprint, jsonify, request

from resources.models import ResourceNode, ResourceType, OreType, ResourceNodeSchema, Inventory, InventorySchema, \
    InventoryToResource, InventoryToResourceSchema
from server import db

resources_bp = Blueprint('resources', __name__, template_folder='templates')


@resources_bp.route('/get/wood')
def get_wood():
    pass

@resources_bp.route('/inventory/create/<int:user_id>')
def create_inventory(user_id):
    my_inventory = Inventory.query.filter_by(user_id=user_id).first()
    if my_inventory is None:
        my_inventory = Inventory()
        my_inventory.user_id = user_id
        db.session.add(my_inventory)
        db.session.commit()
    invs = InventorySchema()
    i = InventoryToResource.query.filter_by(inventory_id=my_inventory.id).first()
    if i is None:
        i = InventoryToResource()
        i.inventory_id = my_inventory.id
        db.session.add(i)
        db.session.commit()
    its = InventoryToResourceSchema()

    return jsonify(inventory=invs.dump(my_inventory),contents=its.dump(i)), 202

@resources_bp.route('/myresources/<int:user_id>')
def my_resources(user_id):
    my_inventory = Inventory.query.filter_by(user_id=user_id).first()
    invs = InventorySchema()
    invs.resource = InventoryToResource.query.get(my_inventory.id)
    return jsonify(data=invs.dump(my_inventory)), 200


@resources_bp.route('/new/<int:land_id>')
def get_new_resource_node(land_id):
    #land_id = request.form['land_id']

    resource = ResourceNode()
    seed()
    resource.available = randint(10, 50)
    resource.type = ResourceType(randint(1, 2))
    if resource.type == ResourceType.ore:
        resource.sub_type = OreType(randint(1, 3))
    else:
        resource.sub_type = OreType.none
    resource.land_id = land_id
    rss = ResourceNodeSchema()
    print(rss.dump(resource))
    db.session.add(resource)
    db.session.commit()

    return jsonify(resource=rss.dump(resource)), 200