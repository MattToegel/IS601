from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from base_model import db


class User(UserMixin, db.Model):
    username = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(150), unique=True, index=True)
    password_hash = db.Column(db.String(150))
    roles = db.relationship("UserRoles", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    name = db.Column(db.String(30), index=True, unique=True)
    users = db.relationship("UserRoles", back_populates="role")


# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object
class UserRoles(db.Model):
    user_id = db.Column(db.ForeignKey('is601_user.id'), primary_key=True)
    right_id = db.Column(db.ForeignKey('is601_role.id'), primary_key=True)
    # extra_data = db.Column(String(50))
    role = db.relationship("Role", back_populates="users")
    user = db.relationship("User", back_populates="roles")