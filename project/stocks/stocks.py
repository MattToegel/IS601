from flask import Blueprint, flash, render_template, request, redirect, url_for
from sql.db import DB  # Import your DB class
from stocks.forms import StockFilterForm, StockForm, StockSearchForm  # Import your StockForm class
from roles.permissions import admin_permission

stocks = Blueprint('stocks', __name__, url_prefix='/stocks', template_folder='templates')

@stocks.route("/fetch", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def fetch():
    form = StockSearchForm()
    if form.validate_on_submit():
        try:
            from utils.AlphaVantage import AlphaVantage
            from utils.lazy import DictToObject
            # Create a new stock record in the database
            result = AlphaVantage.quote(form.symbol.data)
            if result and "symbol" in result.keys():
                result = DictToObject(result)
                print(f"DictToObj {result.__dict__}")
                #result.change_percent = result.change_percent.replace("%","")
                result = DB.insertOne(
                    """INSERT INTO IS601_Stocks (symbol, open, high, low, price, volume, latest_trading_day, previous_close, `change`, change_percent)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        open = VALUES(open),
                        high = VALUES(high),
                        low = VALUES(low),
                        price = VALUES(price),
                        volume = VALUES(volume),
                        latest_trading_day = VALUES(latest_trading_day),
                        previous_close = VALUES(previous_close),
                        `change` = VALUES(`change`),
                        change_percent = VALUES(change_percent)""",
                    result.symbol.upper(), result.open, result.high, result.low, result.price, result.volume, result.latest_trading_day, result.previous_close, result.change, result.change_percent
                )
                if result.status:
                    flash(f"Loaded stock record for {form.symbol.data}", "success")
            else:
                flash(f"No data found for symbol {form.symbol.data}", "warning")
        except Exception as e:
            flash(f"Error loading stock record: {e}", "danger")
    return render_template("stock_search.html", form=form)

@stocks.route("/add", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def add():
    form = StockForm()
    if form.validate_on_submit():
        try:
            # Create a new stock record in the database
            result = DB.insertOne(
                "INSERT INTO IS601_Stocks (symbol, open, high, low, price, volume, latest_trading_day, previous_close, `change`, change_percent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                form.symbol.data.upper(), form.open.data, form.high.data, form.low.data, form.price.data, form.volume.data, form.latest_trading_day.data, form.previous_close.data, form.change.data, form.change_percent.data
            )
            if result.status:
                flash(f"Created stock record for {form.symbol.data}", "success")
        except Exception as e:
            flash(f"Error creating stock record: {e}", "danger")
    return render_template("stock_form.html", form=form, type="Create")

@stocks.route("/edit", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def edit():
    form = StockForm()
    id = request.args.get("id")
    if id is None:
        flash("Missing ID", "danger")
        return redirect(url_for("stocks.list"))
    if form.validate_on_submit() and id:
        try:
            # Update the existing stock record in the database
            result = DB.insertOne(
                "UPDATE IS601_Stocks SET symbol = %s, open = %s, high = %s, low = %s, price = %s, volume = %s, latest_trading_day = %s, previous_close = %s, change = %s, change_percent = %s WHERE id = %s",
                form.symbol.data.upper(), form.open.data, form.high.data, form.low.data, form.price.data, form.volume.data, form.latest_trading_day.data, form.previous_close.data, form.change.data, form.change_percent.data, id
            )
            if result.status:
                flash(f"Updated stock record for {form.symbol.data}", "success")
        except Exception as e:
            flash(f"Error updating stock record: {e}", "danger")
    try:
        result = DB.selectOne(
            "SELECT symbol, open, high, low, price, volume, latest_trading_day, previous_close, `change`, change_percent FROM IS601_Stocks WHERE id = %s",
            id
        )
        if result.status and result.row:
            form = StockForm(data=result.row)
    except Exception as e:
        flash("Error fetching stock record", "danger")
    return render_template("stock_form.html", form=form, type="Edit")

@stocks.route("/list", methods=["GET"])
@admin_permission.require(http_exception=403)
def list():
    searchForm = StockFilterForm(request.args)
    print(searchForm.data)
    query = "SELECT id, symbol, open, high, low, price, volume, latest_trading_day, previous_close, `change`, change_percent FROM IS601_Stocks WHERE 1=1"
    args = {}
    if searchForm.symbol.data:
        query += " AND symbol like %(symbol)s"
        args["symbol"] = f"%{searchForm.symbol.data}%"

    query += " LIMIT 100"
    if searchForm.validate_on_submit():
        pass
    else:
        print(searchForm.errors)
    print(query)
    print(args)
    rows = []
    try:
        result = DB.selectAll(query, args)
        if result.status and result.rows:
            rows = result.rows
    except Exception as e:
        print(e)
        flash("Error getting stock records", "danger")
    return render_template("stocks_list.html", rows=rows, form=searchForm)

@stocks.route("/delete", methods=["GET"])
@admin_permission.require(http_exception=403)
def delete():
    id = request.args.get("id")
    args = {**request.args}
    if id:
        try:
            # Delete the stock record from the database
            result = DB.delete("DELETE FROM IS601_Stocks WHERE id = %s", id)
            if result.status:
                flash("Deleted stock record", "success")
        except Exception as e:
            flash(f"Error deleting stock record: {e}", "danger")
        del args["id"]
    else:
        flash("No ID present", "warning")
    return redirect(url_for("stocks.list", **args))

@stocks.route("/view", methods=["GET"])
def view():
    id = request.args.get("id")
    if id is None:
        flash("Missing ID", "danger")
        return redirect(url_for("stocks.list"))
    try:
        result = DB.selectOne(
            "SELECT symbol, open, high, low, price, volume, latest_trading_day, previous_close, `change`, change_percent FROM IS601_Stocks WHERE id = %s",
            id
        )
        if result.status and result.row:
            return render_template("stock_view.html", stock=result.row)
        else:
            flash("Stock record not found", "danger")
    except Exception as e:
        print(f"Stock error {e}")
        flash("Error fetching stock record", "danger")
    return redirect(url_for("stocks.list"))