import enum

from app import db


class ResourceType(enum.Enum):
    wood = 1
    ore = 2

    def __str__(self):
        return self.name  # value string

    def __html__(self):
        return self.value  # label string


class OreType(enum.Enum):
    none = 0
    copper = 1
    iron = 2
    coal = 3

    def __str__(self):
        return self.name  # value string

    def __html__(self):
        return self.value  # label string


class IngotType(enum.Enum):
    copper = 1
    iron = 2
    steel = 3

    def __str__(self):
        return self.name  # value string

    def __html__(self):
        return self.value  # label string


# resource node can only belong to one land
class ResourceNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    land_id = db.Column(db.Integer, db.ForeignKey('land.id'))
    type = db.Column(db.Enum(ResourceType, create_constraint=False))
    sub_type = db.Column(db.Enum(OreType, create_constraint=False))
    available = db.Column(db.Integer)
    maximum = db.Column(db.Integer)

    def get_availability(self):
        if self.available and self.maximum:
            if self.maximum == 0:
                self.maximum = 1
            return int((self.available/self.maximum)*100)
        return 0

    def is_ore(self):
        return self.type == ResourceType.ore

    def harvest(self, worker):
        n = worker.calc_gather()
        if n > 0:
            self.available -= n
            if self.available <= 0:
                self.available = 0
                db.session.delete(self)
                print('deleted node')
            db.session.commit()
        return n

    def __repr__(self):
        return self.type.name + '-' + self.sub_type.name  # + '[' + str(self.available) + ']'


class InventoryToResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    quantity = db.Column(db.Integer, default=0)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('auth.models.User')
    coins = db.Column(db.Integer, default=0)
    resources = db.relationship('InventoryToResource', cascade="all, delete-orphan")

    def update_coins(self, change):
        self.coins += change
        db.session.commit()
