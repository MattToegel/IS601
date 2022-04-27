from flask import Blueprint, request, render_template, jsonify, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import redirect

from .models import Item, Cart, OrderHistory
from base_model import db

from accounts.models import Transactions

shop = Blueprint('shop', __name__, template_folder='templates', url_prefix='/shop')


@shop.route('/')
def index():
    items = Item.query.filter(Item.stock > 0).limit(50).all()
    return render_template("shop.html", items=items)


# api endpoint (hit via ajax/javascript)
@shop.route("/add-to-cart", methods=["POST"])
@login_required
def add_to_cart():
    item_id = request.form.get("item_id")
    quantity = request.form.get("quantity", default=1, type=int)
    response = {"message": "Unexpected error occurred"}
    if not current_user.is_anonymous:
        if Cart.add_to_cart(item_id, current_user.id, quantity):
            response = {"message": "Added item to cart"}
    else:
        response = {"message": "You must be logged in to add to cart"}
    return jsonify(response)


@shop.route("/view_cart", methods=["GET", "POST"])
@login_required
def view_cart():
    items = []
    if not current_user.is_anonymous:
        print(current_user.id)
        items = Cart.get_user_cart(current_user.id)
    return render_template("cart.html", items=items)


@shop.route("/delete_cart_item", methods=["POST"])
@login_required
def delete_cart_item():
    cart_id = request.form.get("cart_id")
    cart = Cart.query.get(cart_id)
    if cart is not None and cart.user_id == current_user.id:
        db.session.delete(cart)
        try:
            db.session.commit()
            flash("Deleted cart item", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            flash("Error deleting cart item", "danger")
    else:
        flash("Cart item either doesn't exist or you don't own it", "warning")

    return redirect(url_for("shop.view_cart"))


@shop.route("/purchase", methods=["POST"])
@login_required
def purchase():
    items = Cart.get_user_cart(current_user.id)
    total_items = len(items)
    # total_cost = sum(c.item.cost for c in items) or 0
    total_cost = 0
    for ci in items:
        total_cost += int(ci.item.cost)

    balance = current_user.account.balance or 0
    if balance >= total_cost:
        # can afford
        is_valid = True
        next_order_id = db.session.query(func.max(OrderHistory.order_id)).scalar() or 0
        next_order_id = next_order_id + 1
        for c in items:
            if int(c.quantity) <= int(c.item.stock):
                # in stock
                if is_valid:
                    c.item.stock -= int(c.quantity)  # deduct stock
                    # add item to order history
                    oh = OrderHistory()
                    oh.map_cart_item(c, next_order_id, current_user)
                    db.session.delete(c)  # delete processed cart item
            else:
                flash(f"{c.item.name} doesn't have enough stock", "warning")
                is_valid = False
        if is_valid:
            try:
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                print(e)
                flash("Error processing order", "danger")
            # deduct value
            success = Transactions.do_transfer(total_cost, "purchase", current_user.account.id, -1,
                                               f"Purchased {total_items} different items for a total of {total_cost} points")
            if not success:
                db.session.rollback()
                flash("There was a probably completing the purchase", "danger")
            else:
                flash("Purchase successful! Order ID {}".format(next_order_id))
        else:
            db.session.rollback()
    else:
        flash("You can't afford all the items in your cart", "danger")
    return redirect(url_for("shop.view_cart"))
