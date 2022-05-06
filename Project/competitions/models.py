from datetime import datetime, timedelta
from pprint import pprint

from base_model import db
from game.models import IndividualScore
from sqlalchemy import CheckConstraint, func, text, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only, defer, joinedload


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
        try:
            # sometimes a raw sql queries is just easier than managing SQLAlchemy objects (plus it cuts down on # of questions)
            # https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/
            stmt = text("""
                SELECT SUM(score) as score, u.username,u.id FROM is601_individualscore as s
                 JOIN is601_usercomps uc on uc.user_id = s.user_id JOIN is601_user u on u.id = s.user_id 
                 WHERE s.created >= uc.created and s.created <= :expires AND uc.competition_id = :cid
                 GROUP BY s.user_id, u.username ORDER BY score desc LIMIT :limit
            """)
            result = db.session.execute(stmt, {"cid": self.id, "expires": self.expires, "limit": limit})

            pprint("Results {}".format(result))
            r = []
            for row in result:
                print(f"Row {row}")
                r.append(row)
            return r
        except SQLAlchemyError as e:
            print(e)
            return []


class UserComps(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id', 'competition_id'),)
    user_id = db.Column(db.ForeignKey("is601_user.id"))
    competition_id = db.Column(db.ForeignKey("is601_competition.id"))
    user = db.relationship("User", backref="competitions")
    competition = db.relationship("Competition", backref="participants")
