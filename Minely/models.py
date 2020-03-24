from flask_login import UserMixin
from . import db
import enum
# from random import seed
# from random import randint
# seed()


# left gaps for wood types and ore types
class ResourceType(enum.Enum):
    wood = 1
    ore = 2


class OreType(enum.Enum):
    copper = 1
    iron = 2
    coal = 3


class IngotType(enum.Enum):
    copper = 1
    iron = 2
    steel = 3


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(64))


# Land
# workers

# land can only belong to one person
class Land(db.model):
    id = db.column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('uses.id'))


# resource node can only belong to one land
class ResourceNode(db.model):
    id = db.column(db.Integer, primary_ley=True)
    land_id = db.Column(db.Integer, db.ForeignKey('lands.id'))
    type = db.Column(db.Enum(ResourceType))
    sub_type = db.column(db.Enum(OreType))
    available = db.Column(db.Integer)
