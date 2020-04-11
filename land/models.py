from datetime import datetime, timedelta

from app import db


class Land(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resources = db.relationship('ResourceNode', cascade="all, delete-orphan")
    purchase_price = db.Column(db.Integer, default=0)
    user = db.relationship('User')
    cooldown = db.Column(db.SMALLINT, default=5)
    temp_uses = db.Column(db.SMALLINT, default=0)
    lifetime_uses = db.Column(db.Integer, default=0)
    next_action = db.Column(db.DateTime, default=datetime.utcnow())
    density = db.Column(db.Float, default=.1)

    def survey_price(self):
        return int(((self.lifetime_uses + 1) * (self.purchase_price * .15)))

    def sell_price(self):
        return int(self.purchase_price * .75)

    def reset_temp_uses(self):
        self.temp_uses = 0
        db.session.commit()

    def did_search(self):
        if self.can_search():
            if self.temp_uses is None:
                self.temp_uses = 0
            if self.lifetime_uses is None:
                self.lifetime_uses = 0
            if self.cooldown is None:
                self.cooldown = 5  # should just be a temp default
            self.temp_uses += 1
            self.lifetime_uses += 1
            self.next_action = datetime.utcnow() + timedelta(minutes=(self.cooldown * self.temp_uses))
            db.session.commit()

    def can_search(self):
        if self.next_action is None:
            return True
        if datetime.utcnow() >= self.next_action:
            return True
        return False
