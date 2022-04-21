from datetime import datetime, timedelta

from base_model import db
from game.models import IndividualScore
from sqlalchemy import CheckConstraint, func


def current_default(context):
    return context.get_current_parameters()["starting_reward"]


def expires(context):
    days = int(context.get_current_parameters()["duration"])

    return datetime.utcnow() + timedelta(days=days)


class Competition(db.Model):
    name = db.Column(db.String(200))
    min_participants = db.Column(db.Integer, default=3)
    current_participants = db.Column(db.Integer, default=0)
    join_cost = db.Column(db.Integer, default=0)
    payout = db.Column(db.String(12), default="100,0,0")
    starting_reward = db.Column(db.Integer, default=1)
    current_reward = db.Column(db.Integer, default=current_default)
    did_calc = db.Column(db.Boolean, default=False)
    did_payout = db.Column(db.Boolean, default=False)
    duration = db.Column(db.Integer, default=3)
    user_id = db.Column(db.ForeignKey("is601_user.id"))  # creator
    min_score = db.Column(db.Integer, default=1)
    expires = db.Column(db.DateTime, default=expires)
    CheckConstraint("min_score>=1")
    CheckConstraint("starting_reward>=1")
    CheckConstraint("current_reward >= starting_reward")
    CheckConstraint("min_participants>=3")
    CheckConstraint("current_participants >=0")
    CheckConstraint("join_cost >= 0")

    def is_participant(self, user):
        for uc in self.participants:
            if uc.user.id == user.id:
                return True
        return False

    def get_scores(self, limit=10):
        scores = []
        for uc in self.participants:
            uid = uc.user.id

            # https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.value see the deprecation notice for answer
            score = IndividualScore.query.with_entities(func.sum(IndividualScore.score)).filter(
                IndividualScore.created >= uc.created).filter(IndividualScore.created <= self.expires).scalar() or 0
            # score = db.session.query(func.sum(IndividualScore.score)).filter(IndividualScore.created >= uc.created).filter(IndividualScore.created <= self.expires).first()

            scores.append({"username": uc.user.username, "user_id": uid, "score": score})
        scores = sorted(scores, key=lambda i: i['score'], reverse=True)
        """ Standalone attempt (requires joins that are missing at the moment)
        https://docs.sqlalchemy.org/en/14/orm/queryguide.html#selecting-entities-from-subqueries
        query = db.session.query(
                IndividualScore,
                func.rank()
                    .over(
                    order_by=IndividualScore.score.desc(),
                    partition_by=IndividualScore.user_id,
                )
                    .label('rnk')
            ).filter(
                    IndividualScore.created >= uc.created).filter(IndividualScore.created <= self.expires).subquery()
        r = db.session.query(query).filter(text("rnk == 1")).all()
        print(r)
        iscore = aliased(IndividualScore,query)
        stmt = select(iscore).where(text("rnk==1"))
        scores = db.session.execute(stmt).scalars()
        for user_obj in scores:
            print(user_obj)"""
        return scores


class UserComps(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id', 'competition_id'),)
    user_id = db.Column(db.ForeignKey("is601_user.id"))
    competition_id = db.Column(db.ForeignKey("is601_competition.id"))
    user = db.relationship("User", backref="competitions")
    competition = db.relationship("Competition", backref="participants")
