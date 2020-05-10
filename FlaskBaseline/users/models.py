from datetime import datetime

from flask_login import UserMixin

from app import db


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    db.UniqueConstraint('user_id', 'role_id', name='uniq_usr_role')


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(60))
    created = db.Column(db.DateTime, default=datetime.utcnow())
    modified = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    last_login = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('users', lazy='dynamic'), lazy="dynamic")

    def logged_in(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    def has_role(self, role_name):
        role = self.roles.filter_by(name=role_name).first()
        return role is not None