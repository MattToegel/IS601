# used to define common columns across all tables
# we'll follow the design of each table having an id (primary key) column and two timestamps (created, modified)
from datetime import datetime

from flask_sqlalchemy import Model, SQLAlchemy
from sqlalchemy import DateTime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr



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
