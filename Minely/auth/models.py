import enum

from flask_login import UserMixin

from app import db


class Permission(enum.Enum):
    ADMIN = 1
    USER = 2


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(64))
    permission = db.Column(db.Enum(Permission), default=Permission.USER)
    # last_cost = db.Column(db.Integer, default=0)

    land = db.relationship('Land', cascade="all, delete-orphan")
    inventory = db.relationship("Inventory", uselist=False, back_populates="user", cascade="all, delete-orphan")

    def get_coins(self):
        if self.inventory is None:
            print('created user inventory for user_id ' + str(self.id))
            from resources.models import Inventory
            inv = Inventory()
            inv.user_id = self.id
            db.session.add(inv)
            db.session.commit()
        return self.inventory.coins

    def make_purchase(self, cost):
        if self.inventory is not None:
            self.inventory.coins -= cost
            db.session.commit()

    def get_land_cost(self):
        c = len(self.land)
        return (c*c) * 10 # TODO setup base value increment

    def is_admin(self):
        return self.permission == Permission.ADMIN