import enum
from marshmallow.fields import Str
from marshmallow_sqlalchemy.fields import Nested

from app import db, ma



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

    def is_ore(self):
        return self.type == ResourceType.ore

    def __repr__(self):
        return self.type.name + '-' + self.sub_type.name + '[' + str(self.available) + ']'


class InventoryToResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    quantity = db.Column(db.Integer, default=0)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('auth.models.User')
    coins = db.Column(db.Integer, default=0)
    resources = db.relationship('InventoryToResource', cascade="all, delete-orphan")
