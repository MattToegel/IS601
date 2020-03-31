from flask_login import UserMixin
from server import db, ma


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(64))


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        sqla_session = db.session

    id = ma.auto_field()
    email = ma.auto_field()
    name = ma.auto_field()
