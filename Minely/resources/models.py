import enum

from app import db


class Resource(enum.Enum):
    none = 0
    wood = 1
    # ore
    copper_ore = 50
    iron_ore = 51
    coal_ore = 52
    # ingot
    copper_ingot = 100
    iron_ingot = 101
    steel_ingot = 102
    # TODO: Should we put coins here instead of separate column?

    def is_wood(self):
        if 1 >= self.value < 50:
            return True
        return False

    def is_ore(self):
        if 50 >= self.value < 100:
            return True
        return False

    def is_ingot(self):
        if 100 >= self.value < 200:
            return True
        return False

    def is_harvestable(self):
        # TODO lazy "fix" for getting none as harvestable
        if self == Resource.none:
            return False
        if self.is_wood() or self.is_ore():
            return True
        return False

    def __str__(self):
        return self.get_name()  # label string

    def __html__(self):
        # wrapped in string for SelectField, when it pre_validates over enums form has str data
        # but enum has int value
        return str(self.value)  # value string

    def get_name(self):
        return self.name.replace('_', ' ')

    def get_type(self):
        return self.name.split('_')[0]


# resource node can only belong to one land
class ResourceNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    land_id = db.Column(db.Integer, db.ForeignKey('land.id'))
    type = db.Column(db.Enum(Resource, create_constraint=False))
    available = db.Column(db.Integer)
    maximum = db.Column(db.Integer)

    def get_availability(self):
        if self.available and self.maximum:
            if self.maximum == 0:
                self.maximum = 1
            return int((self.available/self.maximum)*100)
        return 0

    def is_ore(self):
        return 'ore' in self.type.name

    def harvest(self, worker):
        n = worker.calc_gather(self.type)
        if n > 0:
            self.available -= n
            if self.available <= 0:
                self.available = 0
                db.session.delete(self)
                print('deleted node')
            db.session.commit()
        return n

    def get_name(self):
        return self.type.name.replace('_', ' ')

    def __repr__(self):
        return self.type.name


class InventoryToResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(Resource, create_constraint=False))
    quantity = db.Column(db.Integer, default=0)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))

    def name(self):
        return self.type.get_name()


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('auth.models.User')
    coins = db.Column(db.Integer, default=0)
    resources = db.relationship('InventoryToResource', cascade="all, delete-orphan", lazy='dynamic')
    smelters = db.relationship('Smelter', cascade="all, delete-orphan", lazy='dynamic')

    def reset_resources(self):
        self.resources.delete()
        db.session.commit()

    def get_quantity(self, resource):
        res = self.resources.filter_by(type=resource).first()
        if res is None or res.quantity is None:
            return 0
        return res.quantity

    def update_coins(self, change):
        self.coins = int( self.coins + change)
        db.session.commit()

    def remove_inventory(self, resource, quantity):
        """pass a positive number to remove"""
        if quantity < 0:
            # quantity is negative and will alter our math
            return False
        res = self.resources.filter_by(type=resource).first()
        if res is None or res.quantity is None:
            # Player doesn't have this item
            return False
        if res.quantity < quantity:
            # Player doesn't have enough of this item
            return False
        res.quantity -= quantity
        db.session.commit()
        return True

    def update_inventory(self, resource, quantity):
        if resource is None:
            print("Invalid inventory item")
        else:
            res = self.resources.filter_by(type=resource).first()
            if res is None:
                res = InventoryToResource()
                res.type = resource
                res.quantity = 0
                res.inventory_id = self.id
                db.session.add(res)
                print('created new resource entry')
            res.quantity += quantity
            # legacy conversion for addition of enum type
            if res.quantity < 0:
                res.quantity = 0
            db.session.commit()



