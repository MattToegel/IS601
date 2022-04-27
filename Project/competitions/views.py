import math
from datetime import datetime

from flask import Blueprint, render_template, flash, request, url_for
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import redirect

from .forms import CompetitionForm
from .models import Competition, UserComps
from base_model import db

from accounts.models import Transactions

comps = Blueprint('comps', __name__, template_folder='templates', url_prefix='/competitions')


@comps.route("/create", methods=["GET", "POST"])
def create_competition():
    form = CompetitionForm()
    if form.validate_on_submit():
        c = Competition()
        form.populate_obj(c)
        cost = c.starting_reward + 1
        cost += c.join_cost
        if current_user.account.balance >= cost:
            c.user_id = current_user.id
            uc = UserComps(user=current_user, competition=c)
            c.current_participants = len(c.participants)
            db.session.add(c)
            did_charge = False
            try:
                if Transactions.do_transfer(cost, "create-comp", current_user.account.id, -1,
                                            f"Created Comp ${c.name}"):
                    did_charge = True
                    db.session.commit()
                    flash("Created competition", "success")
                else:
                    db.session.rollback()

            except SQLAlchemyError as e:
                print(e)
                if did_charge:
                    Transactions.do_transfer(cost, "refund-comp", -1, current_user.account.id,
                                             f"Refund Comp {c.name}")
        else:
            flash(f"Can't afford to create competition. Cost {cost} Balance: {current_user.account.balance}",
                  "danger")
    return render_template("create_competition.html", form=form)


@comps.route("/list")
def list_competitions():
    comps = Competition.query.filter(Competition.expires > datetime.now()).limit(10)
    return render_template("list_competitions.html", comps=comps)


@comps.route("/join", methods=["POST"])
def join_competition():
    id = request.form.get("competition_id", 0, type=int)
    if id > 0:
        c = Competition.query.get(id)
        if c is not None:
            cost = c.join_cost
            if current_user.account.balance >= cost:
                uc = UserComps(user=current_user, competition=c)
                c.current_participants = len(c.participants)
                # TODO calculate current reward
                db.session.add(uc)
                did_charge = False
                try:
                    if Transactions.do_transfer(cost, "create-comp", current_user.account.id, -1,
                                                f"Created Comp ${c.name}"):
                        did_charge = True
                        db.session.commit()
                except SQLAlchemyError as e:
                    print(e)
                    flash("Error joining competition, you may already be a participant", "warning")
                    if did_charge:
                        Transactions.do_transfer(cost, "refund-comp", -1, current_user.account.id,
                                                 f"Refund Comp ${c.name}")
            else:
                flash(
                    f"You can't afford to join this competition. Cost {cost} Balance: {current_user.account.balance}",
                    "warning")
    return redirect(url_for("comps.list_competitions"))


@comps.route("/view")
def view_competition():
    id = request.args.get("id")
    c = Competition.query.get(id)
    return render_template("view_competition.html", c=c)


@comps.route("/winners")
def calc_winners():
    comps = Competition.query.filter(Competition.min_participants<=Competition.current_participants).filter(Competition.expires <= datetime.now()).filter(Competition.did_calc < 1).limit(10)
    for c in comps:
        scores = c.get_scores(3) # top 3
        payout = c.payout.split(",")
        reward = c.current_reward
        fpr = math.ceil(reward * float(payout[0])/100)
        spr = math.ceil(reward * float(payout[1])/100)
        tpr = math.ceil(reward * float(payout[2])/100)
        if fpr > 0:
            Transactions.do_transfer(fpr, "win-comp", -1, scores[0].user.account.id, f"Won 1st in competition {c.name}")
        if spr > 0:
            Transactions.do_transfer(spr, "win-comp", -1, scores[1].user.account.id, f"Won 2nd in competition {c.name}")
        if tpr > 0:
            Transactions.do_transfer(tpr, "win-comp", -1, scores[2].user.account.id, f"Won 3rd in competition {c.name}")
        c.did_calc = 1
        c.did_pay = 1 if (fpr > 0 or spr > 0 or tpr > 0) else 0
