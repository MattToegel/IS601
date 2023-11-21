from flask import Blueprint, flash, render_template, request, redirect, url_for
from sql.db import DB 
from brokers.forms import BrokerForm  
from roles.permissions import admin_permission
from brokerstock_utils.utils import manage_broker_stocks
from utils.lazy import DictToObject
from brokers.models import Broker
from stocks.models import Stock
brokers = Blueprint('brokers', __name__, url_prefix='/brokers', template_folder='templates')
from faker import Faker
import random

def populate_form_with_broker(form, broker):
   # form.process(obj=broker)
    
    form.name.data = broker.name
    form.rarity.data = broker.rarity
    form.life.data = broker.life
    form.power.data = broker.power
    form.defense.data = broker.defense
    form.stonks.data = broker.stonks
    # Clear existing stock entries in the form
    while len(form.stocks.entries) > 0:
        form.stocks.pop_entry()
    for stock in broker.stocks:
        form.stocks.append_entry(stock)
    
    for k,v in form.data.items():
        print(f"{k} - {v}")

def generate_random_broker():
    fake = Faker()
    name = fake.name()
    rarity = random.choices(range(1, 11), weights=[10, 9, 8, 7, 6, 5, 4, 3, 2, 1], k=1)[0]
    broker = Broker(id=None, name=name, rarity=rarity, life=0, power=0, defense=0, stonks=0)
    result = DB.selectAll("SELECT DISTINCT symbol FROM IS601_Stocks")
    stocks = []
    if result.status:
        available_symbols = [row['symbol'] for row in result.rows]
        selected_symbols = random.sample(available_symbols, min(len(available_symbols), rarity))
        placeholders = ",".join(["%s" for x in selected_symbols])
        query = f"""
        SELECT *, 1 as shares FROM IS601_Stocks 
        WHERE symbol in ({placeholders})
        AND IS601_Stocks.latest_trading_day = (
            SELECT MAX(latest_trading_day) FROM IS601_Stocks AS latest_stock
            WHERE latest_stock.symbol = IS601_Stocks.symbol
        )"""
        result = DB.selectAll(query, *selected_symbols)
        if result.status and result.rows:
            print(f"rows: {result.rows}")
            for row in result.rows:
                broker.add_stock(Stock(**row))
    
    broker.recalculate_stats()
    return broker
def create_or_update_broker(form, broker_id=None):
    if not broker_id:
        query = "INSERT INTO IS601_Brokers (Name, Rarity, Life, Power, Defense, Stonks) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (form.name.data, form.rarity.data, form.life.data, form.power.data, form.defense.data, form.stonks.data)

        result = DB.insertOne(query, *values)
        broker_id = result.insert_id
    
    stock_symbols = [{"symbol": entry.symbol.data, "shares": entry.shares.data} for entry in form.stocks]
    manage_broker_stocks(broker_id, stock_symbols)
    broker = fetch_broker_data(broker_id)
    
    if broker_id:
        query = "UPDATE IS601_Brokers SET name = %s, rarity = %s, life = %s, power = %s, defense = %s, stonks = %s WHERE id = %s"
        values = (broker.name, broker.rarity, broker.life, broker.power, broker.defense, broker.stonks, broker_id)
        result = DB.update(query, *values)

        
    return result
def fetch_broker_data(broker_id):
    broker = None
    result = DB.selectOne("SELECT * FROM IS601_Brokers WHERE id = %s", broker_id)
    if result.status and result.row:
        broker = Broker(**result.row)
        stocks = get_associated_stocks(broker.id)
        for stock in stocks:
            broker.add_stock(stock)
        broker.recalculate_stats()
    else:
        print("Broker not found")
        flash("Broker not found", "danger")
    return broker

def get_associated_stocks(broker_id):
    stocks = []
    stock_associations = DB.selectAll(
        """SELECT IS601_Stocks.*, IS601_BrokerStocks.shares FROM IS601_Stocks 
        JOIN IS601_BrokerStocks ON IS601_Stocks.symbol = IS601_BrokerStocks.symbol 
        WHERE IS601_BrokerStocks.broker_id = %s
        AND IS601_Stocks.latest_trading_day = (
            SELECT MAX(latest_trading_day) FROM IS601_Stocks AS latest_stock
            WHERE latest_stock.symbol = IS601_Stocks.symbol
        )
        """, broker_id
    )
        
    if stock_associations.status:
        stocks = [Stock(**stock) for stock in stock_associations.rows]
    return stocks

@brokers.route("/random", methods=["GET", "POST"])
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
    brokers = []
    try:
        result = DB.selectAll("SELECT id, Name, Rarity, Life, Power, Defense, Stonks FROM IS601_Brokers")
        if result.status:
            brokers = result.rows
    except Exception as e:
        flash(f"Error getting broker records: {e}", "danger")
    return render_template("brokers_list.html", rows=brokers)

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
    return render_template("broker_view.html", broker=broker)
