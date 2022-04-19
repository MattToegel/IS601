from flask import Blueprint, request, render_template, jsonify
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from .models import IndividualScore, AccumulativeScore, RegularScore, Inventory
from base_model import db

from accounts.models import Transactions

game = Blueprint('game', __name__, template_folder='templates', url_prefix='/')


@game.route('/game')
def index():
    return render_template("game.html")


# example client -> server save score
@game.route("/api/save_score", methods=["POST"])
@login_required
def save_score():
    score = request.form.get("score", 0, type=int)
    option = request.form.get("option", 1, type=int)
    resp = {"success": False, "message": "Unexpected error"}
    print(f"Score {score}")
    if score > 0:
        s = None
        if option == 1:
            s = IndividualScore(score=score)
            # changed my mind to use option 1
            points = round(score * .01)
            if points > 0:
                Transactions.do_transfer(points, "treasure", -1, current_user.account.id, f"Received {points} points")
                resp["message"] = f"Received {points} points!"
        elif option == 2:
            s = RegularScore(score=score)
        elif option == 3:
            # changed my mind to use option 1
            AccumulativeScore.save_score(score, current_user)
            # example add points
            # points = round(score * .01)
            resp["success"] = True

            # if points > 0:
            # Transactions.do_transfer(points, "treasure", -1, current_user.account.id, f"Received {points} points")
            # resp["message"] = f"Received {points} points!"

        if s is not None:
            s.user = current_user
            db.session.add(s)
            try:
                db.session.commit()
                resp["success"] = True
                resp["message"] = "Saved score"
            except SQLAlchemyError as e:
                db.session.rollback()
                print("Error saving score: {}".format(e))
    print("saved {}".format(resp))
    return jsonify(resp)


@game.route("/scores/top")
def top_scores():
    rtop = RegularScore.get_top_10()
    print(rtop)
    itop = IndividualScore.get_top_10()
    print(itop)
    atop = AccumulativeScore.get_top_10()
    print(atop)
    return render_template("top.html", rtop=rtop, itop=itop, atop=atop)


@game.route("/scores/top/today")
def top_scores_today():
    rtop = RegularScore.get_top_today()
    print(rtop)
    itop = IndividualScore.get_top_today()
    print(itop)
    atop = AccumulativeScore.get_top_today()
    print(atop)
    return render_template("top-today.html", rtop=rtop, itop=itop, atop=atop)


@game.route("/get_inventory")
@login_required
def get_inventory():
    inv = current_user.inventory
    return render_template("inventory.html", inv=inv)


@game.route("/use_item", methods=["POST"])
@login_required
def use_item():
    inventory_id = request.form.get("inventory_id", 0, type=int)
    try:
        if Inventory.use_item(inventory_id):
            return jsonify({"message": "error"})
    except Exception as e:
        print(e)
        return jsonify({"message"}, "Not enough quantity")
    return jsonify({"message": "removed"})
