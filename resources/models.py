import enum
from marshmallow.fields import Str
from marshmallow_sqlalchemy.fields import Nested

from server import db, ma


class ResourceType(enum.Enum):
    wood = 1
    ore = 2


class OreType(enum.Enum):
    none = 0
    copper = 1
    iron = 2
    coal = 3


class IngotType(enum.Enum):
    copper = 1
    iron = 2
    steel = 3


# resource node can only belong to one land
class ResourceNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    land_id = db.Column(db.Integer, db.ForeignKey('land.id'))
    type = db.Column(db.Enum(ResourceType))
    sub_type = db.Column(db.Enum(OreType))
    available = db.Column(db.Integer)


class ResourceNodeSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ResourceNode
        sqla_session = db.session

    id = ma.auto_field()
    land_id = ma.auto_field()
    type = Str()
    sub_type = Str()
    available = ma.auto_field()


class InventoryToResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    quantity = db.Column(db.Integer, default=0)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))


class InventoryToResourceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = InventoryToResource
        sqla_session = db.session

    id = ma.auto_field()
    type = ma.auto_field()
    quantity = ma.auto_field()


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    coins = db.Column(db.Integer, default=0)


class InventorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Inventory
        sqla_session = db.session

    id = ma.auto_field()
    user_id = ma.auto_field()
    coins = ma.auto_field()
    resource = Nested(InventoryToResourceSchema)


