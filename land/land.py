import random

from flask import Blueprint, jsonify, render_template, flash, url_for, redirect
from flask_login import current_user, login_required

from core.forms import PurchaseForm
from core.models import Purchase, PurchaseType
from land.models import Land
from resources.resources import acquire_new_resource
from app import db
land_bp = Blueprint('land', __name__, template_folder='templates')


@land_bp.route('/buy', methods=['GET', 'POST'])
@login_required
def buy_land():
    # we'll get balance/cost for both GET/POST (not gonna trust data from UI)
    balance = current_user.get_coins()
    cost = current_user.get_land_cost()
    form = PurchaseForm()
    if form.validate_on_submit():
        if cost <= balance:
            """_purchase = Purchase()
            _purchase.user_id = current_user.id
            _purchase.cost = cost
            _purchase.purchase_type = PurchaseType.LAND"""
            land = give_land_to_user(current_user.id)
            land.purchase_price = cost
            current_user.make_purchase(cost, PurchaseType.LAND)
            db.session.commit()
            flash("Congratulations! You got another lot")
            return redirect(url_for('land.buy_land')), 302
        else:
            flash("Sorry you can't afford any more land right now")
    form.cost.data = cost
    return render_template('purchase_land.html', form=form, balance=balance), 200


def give_land_to_user(user_id, commit=False):
    land = Land()
    land.user_id = user_id
    land.density = random.uniform(0.05, 1.0)
    db.session.add(land)
    land.resources.append(acquire_new_resource())
    if commit:
        db.session.commit()
    return land


@land_bp.route('/purchase')
def purchase():
    # hey it's free realestate
    if current_user.is_authenticated:
        # TODO make'em pay
        land = give_land_to_user(current_user.id, True)
        return jsonify(id=land.id, user_id=land.user_id), 202
    return {}, 403


@land_bp.route('/lots')
@login_required
def show_my_land():
    myland = Land.query.filter_by(user_id=current_user.id).all()
    return render_template('myland.html', my_land=myland)


@land_bp.route('/search/<int:land_id>')
@login_required
def search_lot_for_resource(land_id):
    land = Land.query.get(int(land_id))
    if land and len(land.resources) == 0:
        if land.can_search():
            land.did_search()
            db.session.commit()
            r = random.uniform(0.0, 1.0)
            if land.density is None:
                # should be temporary as it's calc'ed on new land
                land.density = random.uniform(0.05, 1)
            if r <= land.density:
                resource = acquire_new_resource()
                land.resources.append(resource)

                db.session.commit()
                if resource.is_ore():
                    str = resource.sub_type.name + ' Ore'
                else:
                    str = 'Wood'
                flash("You found " + str)
            else:
                flash("Your search didn't find any resources, better luck next time.")
        else:
            flash("You still need to wait before you can search this lot again.")
    else:
        flash("Your land still has resources, you can't search for more yet")
    return redirect(url_for('land.show_my_land'))


@land_bp.route('/sell/<int:land_id>')
@login_required
def sell(land_id):
    land = Land.query.get(int(land_id))
    if land is not None:
        if land.user_id == current_user.id:
            value = land.sell_price()
            land.user.receive_coins(value)
            db.session.delete(land)
            db.session.commit()
            flash("Successfully sold lot for " + str(value) + " coins")
        else:
            flash("Can't sell a lot that doesn't belong to you.")
    else:
        flash("Couldn't find the particular lot you're trying to sell.")
    return redirect(url_for('land.show_my_land'))