from datetime import datetime

import sqlalchemy as sa
from flask_login import UserMixin
from flask_sqlalchemy import Model, SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.security import generate_password_hash, check_password_hash


# used to define common columns across all tables
# we'll follow the design of each table having an id (primary key) column and two timestamps (created, modified)
class IdModel(Model):
    # https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/mixins.html

    table_prefix = "is601"

    # applies a table prefix in case you're using a shared database (prevents table name collisions)
    @declared_attr
    def __tablename__(cls):
        return cls.table_prefix + "_" + cls.__name__.lower()

    # create an id column that's the primary key of each table
    @declared_attr
    def id(cls):
        for base in cls.__mro__[1:-1]:
            if getattr(base, '__table__', None) is not None:
                type = sa.ForeignKey(base.id)
                break
        else:
            type = sa.Integer

        return sa.Column(type, primary_key=True)

    # create a created timestamp column for each record
    @declared_attr
    def created(cls):
        return sa.Column(DateTime(), default=datetime.utcnow, index=True)

    # create a modified timestamp column for each record that updates when record data changes
    @declared_attr
    def modified(cls):
        return sa.Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow, index=True)


db = SQLAlchemy(model_class=IdModel)


class User(UserMixin, db.Model):
    username = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(150), unique=True, index=True)
    password_hash = db.Column(db.String(150))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
