from app import db


class Land(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resources = db.relationship('ResourceNode', cascade="all, delete-orphan")
    purchase_price = db.Column(db.Integer, default=0)
    user = db.relationship('User')

    def sell_price(self):
        return self.purchase_price * .75
