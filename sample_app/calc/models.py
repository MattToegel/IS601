from base_model import db


class SimpleHistory(db.Model):
    eq = db.Column(db.String(300))
    result = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('is601_user.id')) # need to include the prefix
