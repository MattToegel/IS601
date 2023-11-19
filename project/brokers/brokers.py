from flask import Blueprint, flash, render_template, request, redirect, url_for
from sql.db import DB  # Import your DB class
from brokers.forms import BrokerForm  # Import your BrokerForm class
from roles.permissions import admin_permission
from brokerstock_utils.utils import manage_broker_stocks
from utils.lazy import DictToObject
from brokers.models import Broker
from stocks.models import Stock
brokers = Blueprint('brokers', __name__, url_prefix='/brokers', template_folder='templates')
from faker import Faker
import random
@brokers.route("/random", methods=["GET", "POST"])
def random_broker():
    fake = Faker()
    form = BrokerForm()
    id = None
    if form.validate_on_submit():
        # Save the randomly generated broker
        """name = request.form.get("name")
        rarity = request.form.get("rarity")
        stocks_data = request.form.getlist("stocks")

        # Create stocks instances from stocks data
        stocks = [Stock(**stock) for stock in stocks_data]"""

        result = DB.insertOne(
            "INSERT INTO IS601_Brokers (Name, Rarity, Life, Power, Defense, Stonks) VALUES (%s, %s, %s, %s, %s, %s)",
            form.name.data, form.rarity.data, form.life.data, form.power.data, form.defense.data, form.stonks.data
        )
        if result.status:
            # Manage broker-stock associations
            stock_symbols = [{"symbol":entry.symbol.data, "shares":entry.shares.data} for entry in form.stocks]
            manage_broker_stocks(result.insert_id, stock_symbols)
            id = result.insert_id
            print(f"stock symbols {stock_symbols}")
            print("created broker")
            flash(f"Created broker record for {form.name.data}", "success")
            #return redirect(url_for('brokers.list'))

        #flash("Broker saved successfully!", "success")
        #return redirect(url_for('brokers.list'))
    else:
        # Print form errors to console for debugging
        print("Form Errors:", form.errors)
    # Generate random name and rarity
    name = fake.name()
    rarity = random.choices(range(1, 11), weights=[10, 9, 8, 7, 6, 5, 4, 3, 2, 1], k=1)[0]

    # Fetch distinct stock symbols and pick random ones based on rarity
    result = DB.selectAll("SELECT DISTINCT symbol FROM IS601_Stocks")
    if result.status:
        available_symbols = [row['symbol'] for row in result.rows]
        selected_symbols = random.sample(available_symbols, min(len(available_symbols), rarity))

        broker = Broker(id=None, name=name, rarity=rarity, life=0, power=0, defense=0, stonks=0)
        # Create stocks for the selected symbols
        stocks = []
        for symbol in selected_symbols:
            stock_data = DB.selectOne("SELECT * FROM IS601_Stocks WHERE symbol = %s ORDER BY latest_trading_day DESC LIMIT 1", symbol)
            if stock_data.status and stock_data.row:
                stock = Stock(**stock_data.row)
                stocks.append(stock)
                broker.add_stock(stock)

        # Create a broker with the random data
       
        broker.recalculate_stats()
        form = BrokerForm(obj=broker)
        try:
            # clear all stock items on form
            while form.stocks.pop_entry():
                pass
        except:
            pass
        for stock in stocks:
            form.stocks.append_entry(stock.__dict__)
        if id:
            
            update = DB.insertOne(
            "UPDATE IS601_Brokers SET name = %s, rarity = %s, life = %s, power = %s, defense = %s, stonks = %s WHERE id = %s",
            form.name.data, form.rarity.data, form.life.data, form.power.data, form.defense.data, form.stonks.data, id
        )
            if update.status:
                print("Updated broker stats")
        return render_template("broker_view.html", broker=broker,form=form, save_enabled=True)

    return render_template("broker_view.html", broker=None, save_enabled=False)
@brokers.route("/add", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def add():
    form = BrokerForm()
    
    if form.validate_on_submit():
        print(form)
        try:
           
            # Insert new broker record into the database
            result = DB.insertOne(
                "INSERT INTO IS601_Brokers (Name, Rarity, Life, Power, Defense, Stonks) VALUES (%s, %s, %s, %s, %s, %s)",
                form.name.data, form.rarity.data, form.life.data, form.power.data, form.defense.data, form.stonks.data
            )
            if result.status:
                # Manage broker-stock associations
                stock_symbols = [{"symbol":entry.symbol.data, "shares":entry.shares.data} for entry in form.stocks]
                manage_broker_stocks(id, stock_symbols)
                flash(f"Created broker record for {form.name.data}", "success")
                return redirect(url_for('brokers.list'))
        except Exception as e:
            print(e)
            flash(f"Error creating broker record: {e}", "danger")
    else:
        # Print form errors to console for debugging
        print("Form Errors:", form.errors)
    return render_template("broker_form.html", form=form, type="Create")

def get_stock_associations(id):
    stocks = []
    stock_associations = DB.selectAll(
        """SELECT IS601_Stocks.*, IS601_BrokerStocks.shares FROM IS601_Stocks 
        JOIN IS601_BrokerStocks ON IS601_Stocks.id = IS601_BrokerStocks.stock_id 
        WHERE IS601_BrokerStocks.broker_id = %s
        AND IS601_Stocks.latest_trading_day = (
            SELECT MAX(latest_trading_day) FROM IS601_Stocks AS latest_stock
            WHERE latest_stock.symbol = IS601_Stocks.symbol
        )
        """, id
    )
        
    if stock_associations.status:
        stocks = [Stock(**stock) for stock in stock_associations.rows]
    return stocks
@brokers.route("/edit", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def edit():
    id = request.args.get("id")
    if id is None:
        flash("Missing ID", "danger")
        return redirect(url_for("brokers.list"))
    form = BrokerForm()
    
    if form.validate_on_submit():
        try:
           
            stock_symbols = [{"symbol":entry.symbol.data, "shares":entry.shares.data} for entry in form.stocks]
            manage_broker_stocks(id, stock_symbols)
            flash(f"Updated broker record for {form.name.data}", "success")
            #return redirect(url_for('brokers.list'))
        except Exception as e:
            flash(f"Error updating broker record: {e}", "danger")
    
    result = DB.selectOne(
        "SELECT id, name, rarity, life, power, defense, stonks FROM IS601_Brokers WHERE id = %s", id)
    if result.status and result.row:
        broker = Broker(**result.row)
        
      
        # Load and set the stock associations for the form
        
        stocks = get_stock_associations(id)
        for stock in stocks:
            broker.add_stock(stock)
        broker.recalculate_stats()
        print("Broker Data: " + f"{broker.toJson()}")
        form = BrokerForm(obj=broker)
        update = DB.insertOne(
            "UPDATE IS601_Brokers SET name = %s, rarity = %s, life = %s, power = %s, defense = %s, stonks = %s WHERE id = %s",
            form.name.data, form.rarity.data, form.life.data, form.power.data, form.defense.data, form.stonks.data, id
        )
        if update.status:
            print("Updated broker stats")
        try:
            # clear all stock items on form
            while form.stocks.pop_entry():
                pass
        except:
            pass
        
        for stock in stocks:
            form.stocks.append_entry(stock.__dict__)
    else:
        flash("Broker record not found", "danger")
        return redirect(url_for('brokers.list'))
    broker = DictToObject(result.row)
    return render_template("broker_form.html", form=form, type="Edit", broker=broker)

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
        result = DB.selectOne(
            "SELECT id, name, rarity, life, power, defense, stonks FROM IS601_Brokers WHERE id = %s", id
        )
        if result.status:
            broker = Broker(**result.row)
            stocks = get_stock_associations(id)
            for stock in stocks:
                broker.add_stock(stock)
        else:
            flash("Broker record not found", "danger")
            return redirect(url_for('brokers.list'))
    except Exception as e:
        flash(f"Error fetching broker record: {e}", "danger")
        return redirect(url_for('brokers.list'))
    return render_template("broker_view.html", broker=broker)
