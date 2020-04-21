from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required, current_user

from app import db
from core.forms import PurchaseForm
from core.models import PurchaseType
from resources.models import Resource
from smelt.forms import SmelterForm
from smelt.models import Smelter

smelters_bp = Blueprint('smelt', __name__, template_folder='templates')


@smelters_bp.route('/')
@login_required
def my_smelters():
    smelters = current_user.inventory.smelters.all()
    return render_template("smelters.html", smelters=smelters)


@smelters_bp.route('/buy', methods=['GET', 'POST'])
def buy():
    # we'll get balance/cost for both GET/POST (not gonna trust data from UI)
    cost = current_user.get_smelter_cost()
    form = PurchaseForm()
    balance = current_user.get_coins()
    if form.validate_on_submit():
        if cost <= balance:
            smelter = Smelter()
            current_user.inventory.smelters.append(smelter)
            db.session.add(smelter)
            current_user.make_purchase(cost, PurchaseType.SMELTER)
            db.session.commit()
            flash('Congrats you purchased a new smelter for ' + str(cost) + ' coins!')
            return redirect(url_for('smelt.my_smelters'))
        else:
            flash("Sorry you can't afford to purchase a smelter")

    form.cost.data = cost
    form.submit.label.text = "Purchase"
    return render_template('buy_smelter.html', form=form, balance=balance), 200


@smelters_bp.route('/add/<int:smelter_id>/<string:slot>', methods=['GET', 'POST'])
@login_required
def add_to_smelter(smelter_id, slot):
    # available = current_user.inventory.get_quantity()
    form = SmelterForm()
    if slot == 'primary':
        form.set_options((Resource.copper_ore, Resource.iron_ore))
        # form.set_options((('copper', 'copper'), ('iron', 'iron')))
    elif slot == 'secondary':
        form.set_options((Resource.coal_ore,))
        # form.set_options((('coal', 'coal'),))
    elif slot == 'fuel':
        form.set_options((Resource.wood, Resource.coal_ore))

        # form.set_options((('coal', 'coal'), ('wood', 'wood')))
    if form.validate_on_submit():
        res = form.options.data
        print(res)
        # TODO finish setup
        try:
            q = int(form.quantity.data)
            if q < 1 or q > 50:
                flash("Invalid quantity")
            smelter = Smelter.query.get(int(smelter_id))
            if smelter is not None:
                res = Resource(int(res))
                if slot == 'primary':
                    resp = smelter.add_primary_resource(res, q)
                elif slot == 'secondary':
                    resp = smelter.add_secondary_resource(res, q)
                elif slot == 'fuel':
                    resp = smelter.add_fuel(res, q)
                flash(resp)
        except ValueError:
            pass
    else:
        print(form.errors)

    # messy setup of form due to enum mixing (OreType and ResourceType)

    return render_template("load_smelter.html", form=form, slot=slot)