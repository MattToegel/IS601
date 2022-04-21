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
                db.session.add(uc)
                did_charge = False
                try:
                    if Transactions.do_transfer(cost, "create-comp", current_user.account.id, -1,
                                                f"Created Comp ${c.name}"):
                        did_charge = True
                        db.commit()
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
