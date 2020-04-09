import enum
from datetime import datetime, timedelta
import random

import names
from app import db


class Gender(enum.Enum):
    MALE = 1
    FEMALE = 2

    def __str__(self):
        return self.name  # value string

    def __html__(self):
        return self.value  # label string


class Health(enum.Enum):
    Dead = 0
    Dying = 1
    Sick = 2
    Exhausted = 3
    Ok = 4
    Healthy = 5

    def __str__(self):
        return self.name  # value string

    def __html__(self):
        return self.value  # label string


class Promotion(enum.Enum):
    NONE = 0
    INCREASED_SKILL = 1
    MAXED_SKILL = 2
    INCREASED_EFFICIENCY = 3
    MAXED_EFFICIENCY = 4


class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    skill = db.Column(db.Float)
    efficiency = db.Column(db.Float)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    modified = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    next_action = db.Column(db.DateTime, default=datetime.utcnow())
    gender = db.Column(db.Enum(Gender))
    cooldown = db.Column(db.SMALLINT, default=1)
    temp_uses = db.Column(db.SMALLINT, default=0)
    lifetime_uses = db.Column(db.Integer, default=0)
    health = db.Column(db.Enum(Health), default=Health.Healthy)
    stamina = db.Column(db.SMALLINT, default=100)  # 0 - 100, made better with food
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    promote_cost = db.Column(db.Integer, default=0)
    promote_base = db.Column(db.Integer, default=0)

    def get_promote_cost(self):
        if self.promote_cost == 0 or self.promote_cost is None:
            if self.promote_base == 0 or self.promote_base is None:
                self.promote_base = int(random.uniform(5, 50))
            self.promote_cost = self.promote_base
            db.session.commit()
        return int(self.promote_cost)

    def __determine_promotion(self):
        choices = []
        if self.skill < 1.0:
            choices.append('skill')
        if self.efficiency < 1.0:
            choices.append('ef')
        if len(choices) > 0:
            choice = random.choices(choices)[0]
            if choice == 'skill':
                self.skill += 0.1
                if self.skill > 1.0:
                    self.skill = 1.0
                    return Promotion.MAXED_SKILL
                else:
                    return Promotion.INCREASED_SKILL
            elif choice == 'ef':
                self.efficiency += 0.1
                if self.efficiency > 1.0:
                    self.efficiency = 1.0
                    return Promotion.MAXED_EFFICIENCY
                else:
                    return Promotion.INCREASED_EFFICIENCY
        return Promotion.NONE

    def promote(self, free=False):
        if (self.user.get_coins() >= self.promote_cost) or free:
            # do promote
            promo = self.__determine_promotion()
            if promo is not Promotion.NONE:
                # cache cost
                cost = self.get_promote_cost()
                # raise the price
                self.promote_cost = self.promote_cost * self.promote_cost
                # deduct the cached cost
                if not free:
                    self.user.inventory.update_coins(-cost)
                db.session.commit()
                # succeeded in promote
            # failed to promote
            return promo
        # user can't afford
        return False

    def generate(self, user_id):
        self.skill = random.uniform(0.1, 1.0)
        self.efficiency = random.uniform(0.1, 1.0)
        if bool(random.getrandbits(1)):
            self.gender = Gender.MALE
            self.name = names.get_first_name(gender='male')
        else:
            self.gender = Gender.FEMALE
            self.name = names.get_first_name(gender='female')
        self.user_id = user_id
        self.promote_base = int(random.uniform(5, 50))
        print('Saved to user: ' + str(user_id))
        db.session.add(self)
        db.session.commit()

    def can_gather(self):
        if datetime.utcnow() >= self.next_action:
            return True
        return False

    def reset_temp_uses(self):
        self.temp_uses = 0
        db.session.commit()

    def did_gather(self):
        self.temp_uses += 1
        self.lifetime_uses += 1
        self.next_action = datetime.utcnow() + timedelta(minutes=(self.cooldown*self.temp_uses))
        db.session.commit()

    def get_mod(self):
        ef = self.get_efficiency()
        return ef * self.skill

    def __get_efficiency(self):
        if self.health < Health.Sick:
            return 0
        if self.health == Health.Sick:
            return self.efficiency - (self.efficiency * .75)
        if self.health == Health.Exhausted:
            return self.efficiency - (self.efficiency * .5)
        if self.health == Health.Ok:
            return self.efficiency
        if self.health == Health.Healthy:
            return self.efficiency + (self.efficiency * .1)

    def eat(self, food_increment):
        self.stamina += food_increment
        if self.stamina > 100:
            self.stamina = 100
        db.session.commit()

    def use_stamina(self, decrement=5):
        self.stamina -= decrement
        db.session.commit()