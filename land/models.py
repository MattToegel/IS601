from marshmallow import fields
from marshmallow_sqlalchemy.fields import Nested

from resources.models import ResourceNode
from server import db, ma


# land can only belong to one person
class Land(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class LandSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Land
        sqla_session = db.session

    id = ma.auto_field()
    user_id = ma.auto_field()
    resources = Nested(ResourceNode, many=True, exclude=('land_id',))