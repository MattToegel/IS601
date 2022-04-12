from base_model import db

# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-one
from flask import flash
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError


class Account(db.Model):
    balance = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("is601_user.id"))
    user = db.relationship("User", back_populates="account")

    def refresh(self):
        b = db.session.query(func.sum(Transactions.diff)).filter(Transactions.src == self.id).scalar() or 0
        self.balance = b
        db.session.add(self)
        try:
            db.session.commit()
            print("refreshed account")
        except SQLAlchemyError as e:
            print(e)


class Transactions(db.Model):
    src = db.Column(db.Integer, db.ForeignKey("is601_account.id"))
    dest = db.Column(db.Integer, db.ForeignKey("is601_account.id"))
    diff = db.Column(db.Integer)  # change in balance
    reason = db.Column(db.String(15), index=True)  # transaction type (why it occurred)
    details = db.Column(db.String(240))  # extra user readable details about the transaction

    @staticmethod
    def do_transfer(change, reason, src=-1, dest=-1, details=""):
        # transactions will be two pairs (account losing the value and account gaining the value)
        if change > 0:
            t1 = Transactions(diff=(change * -1), src=src, dest=dest, reason=reason, details=details)
            t2 = Transactions(diff=change, src=dest, dest=src, reason=reason, details=details)
            db.session.add(t1)
            db.session.add(t2)
            try:
                db.session.commit()
                a1 = Account.query.get(src)
                a2 = Account.query.get(dest)
                a1.refresh()
                a2.refresh()
                return True
            except SQLAlchemyError as e:
                print(e)
                flash("Error creating transaction", "danger")
        else:
            flash("Invalid transaction amount", "warning")
        return False
