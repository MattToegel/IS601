import enum
from flask_security import UserMixin, RoleMixin

from app import db
from core.core import CachedStaticProperty
from core.models import Purchase, PurchaseType


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Permission(enum.Enum):
    ADMIN = 1
    USER = 2
    NONE = 10 # can be used to disable users


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(64))
    permission = db.Column(db.Enum(Permission, create_constraint=False), default=Permission.USER)
    # last_cost = db.Column(db.Integer, default=0)

    land = db.relationship('Land', cascade="all, delete-orphan")
    inventory = db.relationship("Inventory", uselist=False, back_populates="user", cascade="all, delete-orphan")
    workers = db.relationship('Worker')
    purchases = db.relationship('Purchase', lazy='dynamic')
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary='roles_users',
                         backref=db.backref('users', lazy='dynamic'))

    def receive_coins(self, coins, auto_commit=False):
        if self.inventory is not None:
            self.inventory.update_coins(coins)
            if auto_commit:
                db.session.commit()

    def get_coins(self):
        if self.inventory is None:
            print('created user inventory for user_id ' + str(self.id))
            from resources.models import Inventory
            inv = Inventory()
            inv.user_id = self.id
            db.session.add(inv)
            db.session.commit()
        else:
            pass
        if self.inventory.coins is None:
            return 0
        return int(self.inventory.coins)

    def make_purchase(self, cost, pt):
        if self.inventory is not None:
            purchase = Purchase()
            purchase.user_id = self.id
            purchase.cost = cost
            purchase.purchase_type = pt
            db.session.add(purchase)
            self.inventory.update_coins(-cost)
            db.session.commit()

    """def make_purchase(self, cost):
        if self.inventory is not None:
            self.inventory.update_coins(-cost)
            db.session.commit()
    """
    def get_land_cost(self):
        c = len(self.land)
        if c == 0:
            # TODO fixes/exploits - free land sell/rebuy to get desired resource node
            purchase = self.purchases.filter_by(purchase_type=PurchaseType.LAND).all()
            if purchase is not None and len(purchase) > 0:
                # if we purchased land at least once we lose the right to the free land
                c = 1
        return (c*c) * 10  # TODO setup base value increment

    def get_hire_cost(self):
        c = len(self.workers)
        if c == 0:
            # TODO will be exploitable if we don't cache the generated worker
            # TODO user would be able to fire/offer transfer and rehire
            # TODO fixes/exploits - free worker hire fire/rehire to get optimal stats
            purchase = self.purchases.filter_by(purchase_type=PurchaseType.WORKER).all()
            if purchase is not None and len(purchase) > 0:
                pass
            else:  # if we never hired a worked then make first one free
                return 0
        cost = 50
        for worker in self.workers:
            cost += worker.promote_base
        return cost

    def get_smelter_cost(self):
        c = len(self.inventory.smelters.all())
        if c == 0:
            return 500
        cost = 500
        return int(cost * c)

    def is_admin(self):
        return self.permission == Permission.ADMIN

    def is_none(self):
        return self.permission == Permission.NONE


    @CachedStaticProperty
    def get_sys_user_id():  # ignore IDE red squiggle, decorator makes it valid
        user_id = 1
        try:
            print('sys user lookup')
            user = User.query.filter_by(name="System").first()
            if user is not None:
                user_id = user.id
        except:
            pass
        print('Sys user: ' + str(user_id))
        return user_id
