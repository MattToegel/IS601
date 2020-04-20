from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_required, current_user

from core.models import PurchaseType
from resources.models import Resource

shop_bp = Blueprint('shop', __name__, template_folder='templates')


@shop_bp.route('/sell')
@shop_bp.route('/sell/<int:resource_id>')
@login_required
def sell(resource_id=None):
    if resource_id is not None:
        res = Resource(resource_id)
        value = 0
        # TODO better lookup table/map
        if res == Resource.wood:
            value = 1
        elif res == Resource.copper_ore:
            value = 1
        elif res == Resource.iron_ore:
            value = 2
        elif res == Resource.coal_ore:
            value = 2
        if value > 0:  # it's ok to sell
            value *= -1  # flip it for gaining cash
            if current_user.inventory.remove_inventory(res, 10):
                current_user.make_purchase(value, PurchaseType.RESOURCE)
                flash("You made " + str(value*-1) + " coins!")
            else:
                flash("You don't have enough " + res.name())
        else:
            flash("Can't sell that here")
        return redirect(url_for("shop.sell"))
    resources = current_user.inventory.resources.all()

    return render_template("shop.html", resources=resources)