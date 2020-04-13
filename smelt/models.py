import enum
from datetime import datetime

from app import db
from resources.models import Resource


class SmelterError(enum.Enum):
    OK = 0
    NOT_ENOUGH_RESOURCES = 1
    BEYOND_CAPACITY = 2
    INVALID_RESOURCE = 3
    UNKNOWN = 10


class Smelter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primary_ore_type = db.Column(db.Enum(Resource, create_constraint=False), default=Resource.none)
    primary_ore_quantity = db.Column(db.SMALLINT, default=0)
    secondary_ore_type = db.Column(db.Enum(Resource, create_constraint=False), default=Resource.none)
    secondary_ore_quantity = db.Column(db.SMALLINT, default=0)
    fuel_type = db.Column(db.String(10), default='')
    fuel_quantity = db.Column(db.SMALLINT, default=0)
    next_action = db.Column(db.DateTime, default=datetime.utcnow())
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    inventory = db.relationship('Inventory')
    assigned_worker = db.Column(db.Integer, db.ForeignKey('worker.id'))  # worker id

    def __update_fuel_quantity(self, fuel_type, quantity):
        # try remove from user inventory
        if fuel_type == 'wood':
            if not self.inventory.remove_inventory('wood', quantity):
                return SmelterError.NOT_ENOUGH_RESOURCES
        elif fuel_type == 'coal':
            if not self.inventory.remove_inventory('coal ore', quantity):
                return SmelterError.NOT_ENOUGH_RESOURCES
        if self.fuel_quantity is None or self.fuel_quantity < 0:
            self.fuel_quantity = 0
        # see if we need to swap fuel types
        if self.fuel_type == fuel_type:
            if self.fuel_quantity + quantity > 50:
                return SmelterError.BEYOND_CAPACITY
            self.fuel_quantity += quantity
            db.session.commit()
            return SmelterError.OK
        else:
            if self.fuel_quantity > 0:
                if self.fuel_type == 'wood':
                    self.inventory.update_inventory('wood', self.fuel_quantity)
                else:
                    self.inventory.update_inventory('coal ore', self.fuel_quantity)
            self.fuel_quantity = quantity
            db.session.commit()
            return SmelterError.OK

    def has_primary(self):
        if self.primary_ore_type is not None and self.primary_ore_type != Resource.none:
            return True
        return False

    def has_secondary(self):
        if self.secondary_ore_type is not None and self.secondary_ore_type != Resource.none:
            return True
        return False

    def has_fuel(self):
        if self.fuel_type is not None and len(self.fuel_type) > 1:
            return True
        return False

    def add_fuel(self, fuel_type, quantity):
        if quantity > 50:
            return SmelterError.BEYOND_CAPACITY
        if quantity <= 0:
            return SmelterError.NOT_ENOUGH_RESOURCES
        if 'coal' in fuel_type:
            return self.__update_fuel_quantity('coal', quantity)
        elif 'wood' in fuel_type:
            return self.__update_fuel_quantity('wood', quantity)

    def add_secondary_resource(self, ore_type, quantity):
        if quantity <= 0:
            return SmelterError.NOT_ENOUGH_RESOURCES
        if quantity > 50:
            return SmelterError.BEYOND_CAPACITY
        if ore_type != Resource.coal:
            # only allow coal for now
            return SmelterError.INVALID_RESOURCE
        if self.secondary_ore_type == ore_type:
            if self.secondary_ore_quantity + quantity > 50:
                return SmelterError.BEYOND_CAPACITY
            if self.inventory.remove_inventory(ore_type + ' ore', quantity):
                self.secondary_ore_quantity += quantity
                db.session.commit()  # TODO commit quantity update
                return SmelterError.OK
            return SmelterError.NOT_ENOUGH_RESOURCES
        self.secondary_ore_type = ore_type
        self.secondary_ore_quantity = quantity
        db.session.commit()  # TODO commit ore set and quantity
        return SmelterError.OK
        return SmelterError.BEYOND_CAPACITY

    def add_primary_resource(self, ore_type, quantity):
        if quantity <= 0:
            return SmelterError.NOT_ENOUGH_RESOURCES
        if quantity > 50:
            return SmelterError.BEYOND_CAPACITY
        if self.primary_ore_type == ore_type:
            if self.primary_ore_quantity + quantity > 50:
                return SmelterError.BEYOND_CAPACITY
            # TODO make sure name concat is matching what's in the DB
            if self.inventory.remove_inventory(ore_type.name + ' ore', quantity):
                # Will be True if resource was remove, False if not
                self.primary_ore_quantity += quantity
                db.session.commit()  # TODO commit quantity update
                return SmelterError.OK
            else:
                return SmelterError.NOT_ENOUGH_RESOURCES
        else:
            # swap resource
            if self.primary_ore_quantity > 0:
                if self.inventory.remove_inventory(ore_type.name + 'ore', quantity):
                    # cache remainder
                    q = self.primary_ore_quantity
                    # update with new quantity
                    self.primary_ore_quantity = quantity
                    # return to player
                    self.inventory.update_inventory(self.primary_ore_type.name + ' ore', q)
                    # swap the ore type
                    self.primary_ore_type = ore_type
                    db.session.commit()  # TODO commit swap/quantity
                    return SmelterError.OK
                else:
                    return SmelterError.NOT_ENOUGH_RESOURCES
            else:
                # reset the ore details if we're 0 or less, shouldn't happen but being safe
                self.primary_ore_type = Resource.none
                self.primary_ore_quantity = 0
                db.session.commit()  # TODO save reset
                # run it through the function again now that we cleared up the ore type
                return self.add_primary_resource(ore_type, quantity)

    def assign(self, worker):
        self.assigned_worker = worker.id
        # TODO assign after did_gather since new logic will
        # make can_gather false if assigned_to_smelter is > 0
        worker.did_gather()
        worker.assigned_to_smelter = self.id
        worker.smelter = self
        # TODO calc things

    def is_ready(self):
        if datetime.utcnow() >= self.next_action:
            return True
        return False

    def unassign(self, worker):
        if self.assigned_worker == worker.id:
            if self.is_ready():
                # TODO reward worker
                # give resources to player
                self.worker.remove_from_smelter()
                self.assigned_worker = 0
                return True  # job's done
            return False  # time still remaining
        worker.remove_from_smelter()
        return True  # different worker assigned

    def smelt(self):
        if self.ore_type == Resource.none:
            pass