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
    form = PurchaseForm()
    balance = current_user.get_coins()
    if form.validate_on_submit():
        cost = current_user.get_land_cost()
        if cost <= balance:
            _purchase = Purchase()
            _purchase.user_id = current_user.id
            _purchase.cost = cost
            _purchase.purchase_type = PurchaseType.LAND
            land = give_land_to_user(current_user.id)
            current_user.make_purchase(cost)
            db.session.commit()
            balance = current_user.get_coins()
            flash("Congradulations! You got another lot")
        else:
            flash("Sorry you can't afford any more land right now")
    else:
        pass
    form.cost.data = current_user.get_land_cost()
    return render_template('purchase_land.html', form=form, balance=balance), 200


def give_land_to_user(user_id, commit=False):
    land = Land()
    land.user_id = user_id
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
        resource = acquire_new_resource()
        land.resources.append(resource)
        db.session.commit()
        flash("Yay you found " + ('Ore' if resource.is_ore() else 'Wood'))
    else:
        flash("Your land still has resources, you can't search for more yet")
    return redirect(url_for('land.show_my_land'))


@land_bp.route('/sell/<int:land_id>')
def sell(land_id):

    return redirect(url_for('land.show_my_land'))