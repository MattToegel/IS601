from flask import Blueprint, flash, render_template, request, redirect, url_for
from sql.db import DB 
from brokers.forms import BrokerForm, PurchaseForm, BrokerSearchForm,BrokerUpgradeForm
from roles.permissions import admin_permission
from brokerstock_utils.utils import manage_broker_stocks
from utils.lazy import DictToObject
from brokers.models import Broker
from stocks.models import Stock
brokers = Blueprint('brokers', __name__, url_prefix='/brokers', template_folder='templates')

from flask_login import current_user, login_required
from points.points import change_points
from brokerstock_utils.utils import *

def filter_search(form, allowed_columns):
    where = ""
    args = {}
    if form.name.data:
        where += " AND name LIKE %(name)s"
        args["name"] = f"%{form.name.data}%"
    if form.rarityMin.data:
        where += " AND rarity >= %(rmin)s"
        args["rmin"] = form.rarityMin.data
    if form.rarityMax.data:
        where += " AND rarity <= %(rmax)s"
        args["rmax"] = form.rarityMax.data
    if form.sort.data in allowed_columns and form.order.data in ["asc","desc"]:
        where += f" ORDER BY {form.sort.data} {form.order.data}"
    else:
        where += " ORDER BY name asc"
    return (where, args)

@brokers.route("/upgrade", methods=["POST"])
@login_required
def upgrade():
    form = BrokerUpgradeForm()
    broker_id = -1
    print(form.data)
    if form.validate_on_submit():
        broker_id = form.broker_id.data
        user_id = current_user.id
        # check ownership
        result = DB.selectOne("SELECT id FROM IS601_UserBrokers WHERE broker_id = %(broker_id)s and user_id = %(user_id)s",{
            "broker_id":broker_id,
            "user_id": user_id
        })
        if result.status and result.row:
            symbol = form.symbol.data
            # get price
            result = DB.selectOne("SELECT price FROM IS601_Stocks WHERE symbol = %(symbol)s ORDER BY modified desc LIMIT 1",{
                "symbol":symbol
            })
            if result.status and result.row:
                # check afforability
                price = int(result.row["price"])
                shares = int(form.shares.data)
                total = price * shares
                if total <= current_user.points:
                    if change_points(current_user.id, -total):
                        # increase the shares, includes extra sub query to double check it's only an owned Broker
                        result = DB.update("""UPDATE IS601_BrokerStocks set shares = shares + %(shares)s 
                                WHERE broker_id = (SELECT broker_id FROM
                                IS601_UserBrokers WHERE broker_id = %(broker_id)s AND user_id = %(user_id)s)
                                AND symbol = %{symbol}""",{
                                "broker_id":broker_id,
                                "user_id": user_id,
                                "shares":shares,
                                "symbol": symbol
                            })
                        if result.status: # success
                           flash(f"Added {shares} more {'shares' if shares > 1 else 'share'} of {symbol}","success")
                        else: # update failed, refund
                            change_points(current_user.id, total)
                            flash("There was a problem upgrading; refunding the cost", "warning")
                    else: # payment failed, likely can't afford, but we already check prior
                        flash("An unhandled error happened", "danger")
                else:
                    flash(f"You can't afford to spend {total} points on {shares} of {symbol}","warning")
        else:
            flash("You can't buy shares for a Broker you don't own", "danger")
    else:
        flash(form.errors)
    if int(broker_id) < 1:
        return redirect(url_for("brokers.team"))
    return redirect(url_for("brokers.view", id=broker_id))

@brokers.route("/team", methods=["GET"])
@login_required
def team():
    form = BrokerSearchForm(request.args)
    user_id = request.args.get("id", current_user.id)
    allowed_columns = ["name", "rarity", "life", "power", "defense", "stonks"]
    form.sort.choices = [(k,k) for k in allowed_columns]
    query = """SELECT b.id, name, rarity, life, power, defense, stonks FROM IS601_Brokers b 
    JOIN IS601_UserBrokers ub on ub.broker_id = b.id WHERE ub.user_id = %(user_id)s"""
    where = filter_search(form, allowed_columns)
    args = where[1]
    where = where[0]
    page = request.args.get("page") or 1
    try:
        page = int(page)
        if page < 1:
            page = 1
    except:
        page = 1
    per_page = 10
    offset = (page-1)*per_page
    where += " LIMIT %(offset)s, %(limit)s"
    args["offset"] = offset
    args["limit"] = per_page
    args["user_id"] = user_id
    brokers = []
    try:
        result = DB.selectAll(query+where, args)
        if result.status:
            brokers = result.rows
    except Exception as e:
        flash(f"Error getting broker records: {e}", "danger")
    return render_template("brokers_list.html", rows=brokers, form=form)

@brokers.route("/purchase", methods=["GET","POST"])
def purchase():
    form = PurchaseForm()
    cost = 50
    if form.validate_on_submit():
        if current_user.get_points() >= cost:
            status = change_points(current_user.id, -cost)
            if status:
                query = """ 
                SELECT id FROM IS601_Brokers b where id 
                not in (SELECT id FROM IS601_UserBrokers WHERE broker_id = b.id) 
                ORDER BY rand() LIMIT 1
                """
                result = DB.selectOne(query)
                if result.status and result.row:
                    broker_id = result.row["id"]
                    query = """ INSERT INTO IS601_UserBrokers (user_id, broker_id, is_active)
                    VALUES (%(user_id)s, %(broker_id)s, 1)"""
                    result = DB.insertOne(query,{
                        "user_id":current_user.id,
                        "broker_id":broker_id
                    })
                    flash("You got it!", "success")
                    return redirect(url_for("brokers.view", id=broker_id))
                else:
                    flash("No Broker available, here's your cash back", "warning")
                    change_points(current_user.id, cost)
        else:
            flash("You're broke buddy", "danger")
    return render_template("purchase_broker.html",form=form)

@brokers.route("/random", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def random_broker():
    
    form = BrokerForm()

    if form.validate_on_submit():
        result = create_or_update_broker(form)
        if result.status:
            flash(f"Created broker record for {form.name.data}", "success")
            #return redirect(url_for('brokers.list'))
    else:
        print("Form Errors:", form.errors)
    broker = generate_random_broker()
    populate_form_with_broker(form, broker)
    return render_template("broker_view.html", broker=broker, form=form, save_enabled=True)

    #return render_template("broker_view.html", broker=None, save_enabled=False)

@brokers.route("/add", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def add():
    form = BrokerForm()
    
    if form.validate_on_submit():
        result = create_or_update_broker(form)
        if result.status:
            flash(f"Created broker record for {form.name.data}", "success")
        else:
            flash(f"Error creating broker record: {result.error}", "danger")
    else:
        print("Form Errors:", form.errors)
    return render_template("broker_form.html", form=form, type="Create")

@brokers.route("/edit", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def edit():
    form = BrokerForm()
    id = request.args.get("id")
    if id is None:
        flash("Missing ID", "danger")
        return redirect(url_for("brokers.list"))
    if form.validate_on_submit():
        result = create_or_update_broker(form, broker_id=id)
        if result.status:
            flash(f"Updated broker record for {form.name.data}", "success")
        else:
            flash(f"Error updating broker record: {result.error}", "danger")
    else:
        print("Form Errors:", form.errors)
    broker = fetch_broker_data(id)
    populate_form_with_broker(form, broker)
    return render_template("broker_form.html", form=form,broker=broker, type="Edit")

@brokers.route("/list", methods=["GET"])
@admin_permission.require(http_exception=403)
def list():
    form = BrokerSearchForm()
    brokers = []
    try:
        allowed_columns = ["name", "rarity", "life", "power", "defense", "stonks"]
        form.sort.choices = [(k,k) for k in allowed_columns]
        query = """SELECT b.id, name, rarity, life, power, defense, stonks, if(ub.user_id > 0, 'unavailable','available') as status FROM IS601_Brokers b 
        LEFT JOIN IS601_UserBrokers ub on ub.broker_id = b.id WHERE 1=1"""
        where = filter_search(form, allowed_columns)
        args = where[1]
        where = where[0]
        page = request.args.get("page") or 1
        try:
            page = int(page)
            if page < 1:
                page = 1
        except:
            page = 1
        per_page = 10
        offset = (page-1)*per_page
        where += " LIMIT %(offset)s, %(limit)s"
        args["offset"] = offset
        args["limit"] = per_page
        result = DB.selectAll(query + where, args)
        if result.status:
            brokers = result.rows
    except Exception as e:
        flash(f"Error getting broker records: {e}", "danger")
    return render_template("brokers_list.html", rows=brokers, form=form)

@brokers.route("/delete", methods=["GET"])
@admin_permission.require(http_exception=403)
def delete():
    id = request.args.get("id")
    if id is None:
        flash("Missing ID", "danger")
        return redirect(url_for("brokers.list"))
    try:
        result = DB.delete("DELETE FROM IS601_BrokerStocks WHERE broker_id = %s", id)
        result = DB.delete("DELETE FROM IS601_Brokers WHERE id = %s", id)
        if result.status:
            flash("Deleted broker record", "success")
    except Exception as e:
        flash(f"Error deleting broker record: {e}", "danger")
    return redirect(url_for("brokers.list"))

@brokers.route("/view", methods=["GET"])
def view():
    id = request.args.get("id")
    stockForm = BrokerUpgradeForm()
    if id is None:
        flash("Missing ID", "danger")
        return redirect(url_for("brokers.list"))
    broker = None
    try:
        broker = fetch_broker_data(id)
        if not Broker:
            return redirect(url_for('brokers.list'))
    except Exception as e:
        flash(f"Error fetching broker record: {e}", "danger")
        return redirect(url_for('brokers.list'))
    return render_template("broker_view.html", broker=broker, stockForm=stockForm)
