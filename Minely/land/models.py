from marshmallow import fields
from marshmallow_sqlalchemy.fields import Nested


from app import db, ma


# land can only belong to one person
from resources.models import ResourceNode


class Land(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resources = db.relationship(ResourceNode, cascade="all, delete-orphan")

    user = db.relationship('User')