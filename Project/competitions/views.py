import math
from datetime import datetime

from flask import Blueprint, render_template, flash, request, url_for, jsonify
from flask_login import current_user
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import redirect

from auth.models import User
from .forms import CompetitionForm
from .models import Competition, UserComps
from base_model import db

from accounts.models import Transactions

comps = Blueprint('comps', __name__, template_folder='templates', url_prefix='/competitions')


@comps.route("/create", methods=["GET", "POST"])
def create_competition():
    form = CompetitionForm()

    if form.validate_on_submit():
        print("processing form")
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
                    flash("Payment for creating competition failed", "danger")
                    print("Transaction failed")

            except SQLAlchemyError as e:
                print(f"Create competition error: {e}")
                if did_charge:
                    if Transactions.do_transfer(cost, "refund-comp", -1, current_user.account.id,
                                                f"Refund Comp {c.name}"):
                        flash("Refunded competition cost", "warning")

        else:
            flash(f"Can't afford to create competition. Cost {cost} Balance: {current_user.account.balance}",
                  "danger")
            print("cant afford")
    return render_template("create_competition.html", form=form)


@comps.route("/list")
def list_competitions():
    comps = Competition.query.filter(Competition.expires > datetime.now()).order_by(Competition.expires.asc()).limit(10)
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
    response = {"competitions": [], "invalid": 0}
    calc_comps = Competition.query.filter(Competition.min_participants <= Competition.current_participants).filter(
        Competition.expires <= datetime.now()).filter(Competition.did_calc < 1).limit(10)
    for c in calc_comps:
        scores = c.get_scores(3)  # top 3
        payout = c.payout.split(",")
        reward = c.current_reward
        fpr = math.ceil(reward * float(payout[0]) / 100)
        spr = math.ceil(reward * float(payout[1]) / 100)
        tpr = math.ceil(reward * float(payout[2]) / 100)
        comp = {"name": c.name, "payout": [], "did_calc": 0, "did_payout": 0}
        if fpr > 0:
            account_id = User.query.get(scores[0].user_id).account.id
            Transactions.do_transfer(fpr, "win-comp", -1, account_id, f"Won 1st in competition {c.name}")
            comp["payout"].append({
                "place": "first",
                "user": scores[0].username,
                "won": fpr
            })
        if spr > 0:
            account_id = User.query.get(scores[1].user_id).account.id
            Transactions.do_transfer(spr, "win-comp", -1, account_id, f"Won 2nd in competition {c.name}")
            comp["payout"].append({
                "place": "second",
                "user": scores[1].username,
                "won": spr
            })
        if tpr > 0:
            account_id = User.query.get(scores[2].user_id).account.id
            Transactions.do_transfer(tpr, "win-comp", -1, account_id, f"Won 3rd in competition {c.name}")
            comp["payout"].append({
                "place": "third",
                "user": scores[2].username,
                "won": tpr
            })
        c.did_calc = 1
        c.did_payout = 1 if (fpr > 0 or spr > 0 or tpr > 0) else 0
        comp["did_payout"] = c.did_payout
        comp["did_calc"] = c.did_calc;
        response["competitions"].append(comp)
        db.session.add(c)

    # commit the batch of payout/competition updates
    try:
        db.session.commit()
        print("Saved payouts")
    except SQLAlchemyError as e:
        print(f"Error saving calced competitions {e}")
    # close invalid competitions
    stmt = text("""
    UPDATE is601_competition set did_calc = 1 WHERE did_calc = 0 AND min_participants > current_participants AND NOW() <= expires
    """)
    try:
        result = db.session.execute(stmt)
        db.session.commit()
        response["invalid"] = result.rowcount
        print(f"Closed {result.rowcount} invalid competitions")
    except SQLAlchemyError as e:
        print(f"Error closing invalid accounts {e}")
    return jsonify(response)
