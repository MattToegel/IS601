from datetime import datetime, time, timezone

from base_model import db
from sqlalchemy import desc, func, and_
from sqlalchemy.exc import SQLAlchemyError


# since query returns rows and not the object
# I need to map the result so that it follows the same structure as the other samples
def ind_mapper(x):
    d = x._asdict()
    print(d["IndividualScore"])
    r = x._asdict()["IndividualScore"]  # change row to IndividualScore
    r.score = d["tScore"]  # apply the summed score to the object (don't add/commit this to DB)
    return r


class Inventory(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id', 'item_id'),)
    item_id = db.Column(db.ForeignKey("is601_item.id"))
    item = db.relationship("Item", backref="inventory")
    user_id = db.Column(db.ForeignKey("is601_user.id"))
    user = db.relationship("User", backref="inventory")
    quantity = db.Column(db.Integer, default=0)

    @staticmethod
    def add_item(item, user, quantity=1):
        inv = Inventory(item=item, user=user, quantity=1)
        db.session.add(inv)
        try:
            db.session.commit()
            print("Added to inventory")
        except SQLAlchemyError as e:
            print(e)
            existing_inv = Inventory.query.filter_by(item_id=item.id).filter_by(user_id=user.id).first()
            existing_inv.quantity += quantity
            try:
                db.session.commit()
                print("Updated inventory")
            except SQLAlchemyError as e:
                print(e)


# Made the decision to use this version of scores 04/18/2022
class IndividualScore(db.Model):
    # this example is for games that have an upper limit score like if it plays to 10
    # then an individual record is added, but upon getting the results the scores get SUM'ed for each person
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("is601_user.id"))
    user = db.relationship("User", back_populates="iscores", primaryjoin="User.id == IndividualScore.user_id")

    @staticmethod
    def get_top_10():
        return list(
            map(ind_mapper, db.session.query(IndividualScore, func.Sum(IndividualScore.score).label("tScore")).group_by( \
                IndividualScore.user_id) \
                .order_by(desc("tScore")).limit(10).all()))
        # return IndividualScore.query.order_by(IndividualScore.score.desc(), IndividualScore.created.desc()).limit(10).all()

    @staticmethod
    def get_latest_scores(user_id):
        if user_id is not None:
            return IndividualScore.query.filter(IndividualScore.user_id == user_id).order_by(
                IndividualScore.created.desc()).limit(10).all()
        return []

    @staticmethod
    def get_top_today():
        eod = datetime.combine(datetime.now(), time.max).astimezone(timezone.utc)
        bod = datetime.combine(datetime.now(), time.min).astimezone(timezone.utc)
        print(eod)
        print(bod)
        return list(
            map(ind_mapper, db.session.query(IndividualScore, func.Sum(IndividualScore.score).label("tScore")).filter(
                and_(IndividualScore.created >= bod, IndividualScore.created <= eod)).group_by(
                IndividualScore.user_id).order_by(desc("tScore")).limit(10).all()))


class RegularScore(db.Model):
    # this example is regular old school arcade style
    # it assumes a wide range of scores are potential
    # and each completed play records that sessions score
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("is601_user.id"))
    user = db.relationship("User", back_populates="scores")

    @staticmethod
    def get_top_10():
        return RegularScore.query.order_by(RegularScore.score.desc(), RegularScore.created.desc()).limit(10).all()

    @staticmethod
    def get_latest_scores(user_id):
        if user_id is not None:
            return RegularScore.query.filter(RegularScore.user_id == user_id).order_by(
                RegularScore.created.desc()).limit(10).all()
        return []

    @staticmethod
    def get_top_today():
        eod = datetime.combine(datetime.now(), time.max).astimezone(timezone.utc)
        bod = datetime.combine(datetime.now(), time.min).astimezone(timezone.utc)
        return RegularScore.query.filter(and_(RegularScore.created >= bod, RegularScore.created <= eod)).order_by(
            RegularScore.score.desc(), RegularScore.created.desc()).limit(10).all()


class AccumulativeScore(db.Model):
    # this example is an alternative to individual score where each
    # player has one score reference and each update just increases this running total
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("is601_user.id"), unique=True)
    user = db.relationship("User", back_populates="ascores")

    @staticmethod
    def save_score(score, user):
        ascore = AccumulativeScore.query.filter(AccumulativeScore.user_id == user.id).first()
        if ascore is None:
            ascore = AccumulativeScore(score=score)
            ascore.user = user
        else:
            ascore.score += int(score)
        db.session.add(ascore)
        try:
            db.session.commit()
            print("saved score")
        except SQLAlchemyError as e:
            print(e)

    @staticmethod
    def get_top_10():
        return AccumulativeScore.query.order_by(AccumulativeScore.score.desc(), AccumulativeScore.created.desc()).limit(
            10).all()

    @staticmethod
    def get_latest_scores(user_id):
        if user_id is not None:
            return AccumulativeScore.query.filter(AccumulativeScore.user_id == user_id).order_by(
                AccumulativeScore.created.desc()).limit(10).all()
        return []

    @staticmethod
    def get_top_today():
        eod = datetime.combine(datetime.now(), time.max).astimezone(timezone.utc)
        bod = datetime.combine(datetime.now(), time.min).astimezone(timezone.utc)
        return AccumulativeScore.query.filter(
            and_(AccumulativeScore.created >= bod, AccumulativeScore.created <= eod)).order_by(
            AccumulativeScore.score.desc(), AccumulativeScore.created.desc()).limit(
            10).all()
