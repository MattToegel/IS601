from flask import Blueprint, flash, render_template, request, redirect, url_for, current_app
from sql.db import DB
from roles.permissions import admin_permission
from cards.forms import CardFetchForm, CardForm, CardSearchForm,AdminCardSearchForm, AssocForm
from utils.HearthstoneAPI import Hearthstone
from sql.db import DB
from utils.lazy import DictToObject
from flask_login import current_user, login_required
cards = Blueprint('cards', __name__, url_prefix='/cards',template_folder='templates')

cache = current_app.cache
#@cache.cached(timeout=30) # cache for 30 seconds since this is expensive
def get_rarities():
    results = DB.selectAll("SELECT DISTINCT rarity as label FROM IS601_Quick_Cards WHERE rarity != ''")
    r = []
    if results.status and results.rows:
        r = results.rows
    return r

#@cache.cached(timeout=30) # cache for 30 seconds since this is expensive
def get_classes():
    results = DB.selectAll("SELECT DISTINCT card_class as label FROM IS601_Quick_Cards WHERE card_class != ''")
    r = []
    if results.status and results.rows:
        r = results.rows
    return r

#@cache.cached(timeout=30) # cache for 30 seconds since this is expensive
def get_types():
    results = DB.selectAll("SELECT DISTINCT card_type as label FROM IS601_Quick_Cards WHERE card_type != ''")
    r = []
    if results.status and results.rows:
        r = results.rows
    return r

#@cache.cached(timeout=30) # cache for 30 seconds since this is expensive
def get_sets():
    results = DB.selectAll("SELECT DISTINCT card_set as label FROM IS601_Quick_Cards WHERE card_set != ''")
    r = []
    if results.status and results.rows:
        r = results.rows
    return r

#@cache.cached(timeout=30) # cache for 30 seconds since this is expensive
def get_schools():
    results = DB.selectAll("SELECT DISTINCT spell_school as label FROM IS601_Quick_Cards WHERE spell_school != ''")
    r = []
    if results.status and results.rows:
        r = results.rows
    return r

insert_query = """INSERT INTO IS601_Quick_Cards
                (name, text, flavor_text, mana_cost, rarity, card_class, card_type, card_set, spell_school, source)
                VALUES (%(name)s, %(text)s, %(flavor_text)s, %(mana_cost)s, %(rarity)s, %(card_class)s, %(card_type)s, %(card_set)s, %(spell_school)s, %(source)s)
                ON DUPLICATE KEY UPDATE name = VALUES(name), text = VALUES(text), flavor_text = VALUES(flavor_text),
                mana_cost = VALUES(mana_cost), rarity = VALUES(rarity), card_class = VALUES(card_class), card_type = VALUES(card_type), card_set = VALUES(card_set), spell_school = VALUES(spell_school), source = VALUES(source)"""

def get_total(partial_query, args={}):
    total = 0
    try:
        result = DB.selectOne("SELECT count(1) as total FROM "+partial_query, args)
        if result.status and result.row:
            total = int(result.row["total"])
    except Exception as e:
        print(f"Error getting total {e}")
        total = 0
    return total

@cards.route("/fetch", methods=["GET","POST"])
@admin_permission.require(http_exception=403)
def fetch():
    form = CardFetchForm()
    if form.validate_on_submit():
        page = form.page.data
        page_size = form.page_size.data
        if page >= 1 and page_size >= 1:
            api_results = Hearthstone.get_cards(page, page_size)
            if api_results:
                try:
                    result = DB.insertMany(insert_query, api_results)
                    if result.status:
                        flash("Loaded in records", "success")
                except Exception as e:
                    print(f"Error inserting into cards table {e}")
                    flash("There was an error inserting the data", "danger")
                
    return render_template("card_fetch.html", form=form)

@cards.route("/add", methods=["GET","POST"])
@admin_permission.require(http_exception=403)
def add():
    form = CardForm()
    rarities = [(k["label"], k["label"]) for k in get_rarities()]
    form.rarity.choices = rarities

    card_class = [(k["label"], k["label"]) for k in get_classes()]
    form.card_class.choices = card_class

    card_type = [(k["label"], k["label"]) for k in get_types()]
    form.card_type.choices = card_type

    card_set = [(k["label"], k["label"]) for k in get_sets()]
    form.card_set.choices = card_set

    spell_school = [(k["label"], k["label"]) for k in get_schools()]
    form.spell_school.choices = spell_school
    if form.validate_on_submit():
        data = form.data
        # convert form data into query args dict
        del data["submit"]
        del data["csrf_token"]
        data["source"] = "manual"
        try:
            result = DB.insertOne(insert_query,data)
            if result.status:
                flash("Added new card", "success")
        except Exception as e:
            print(f"Error adding new card into cards table {e}")
            flash("There was an error inserting the data", "danger")
    return render_template("card_manage.html", form=form, type="Create")

@cards.route("/edit", methods=["GET","POST"])
@admin_permission.require(http_exception=403)
def edit():
    id = request.args.get("id")
    if not id:
        flash("Invalid id", "danger")
        pass
    form = CardForm()
    rarities = [(k["label"], k["label"]) for k in get_rarities()]
    form.rarity.choices = rarities

    card_class = [(k["label"], k["label"]) for k in get_classes()]
    form.card_class.choices = card_class

    card_type = [(k["label"], k["label"]) for k in get_types()]
    form.card_type.choices = card_type

    card_set = [(k["label"], k["label"]) for k in get_sets()]
    form.card_set.choices = card_set

    spell_school = [(k["label"], k["label"]) for k in get_schools()]
    form.spell_school.choices = spell_school
    if form.validate_on_submit():
        data = form.data
        # convert form data into query args dict
        del data["submit"]
        del data["csrf_token"]
        data["source"] = "manual"
        try:
            result = DB.insertOne(insert_query,data)
            if result.status:
                flash("Updated card", "success")
        except Exception as e:
            print(f"Error updating card in cards table {e}")
            flash("There was an error updating the data", "danger")
    result = DB.selectOne("SELECT name, text, flavor_text, mana_cost, rarity, card_class, card_type, card_set,spell_school FROM IS601_Quick_Cards WHERE id = %s", id)
    
    if result.status and result.row:
        data = DictToObject(result.row)
        form.process(obj=data)

        print(f"Loaded form: {form.data}")
    return render_template("card_manage.html", form=form, type="Edit")

@cards.route("/view", methods=["GET"])
def view():
    id = request.args.get("id")
    if not id:
        flash("Missing id", "danger")
    else:
        try:
            result = DB.selectOne("""SELECT name, text, flavor_text, mana_cost, rarity, card_class, card_type, card_set,spell_school, 
            IFNULL((SElECT count(1) FROM IS601_Quick_WatchList WHERE user_id = %(user_id)s and card_id = IS601_Quick_Cards.id), 0) as 'is_assoc' 
            FROM IS601_Quick_Cards WHERE id = %(card_id)s""", {"card_id": id, "user_id": current_user.id})
            if result.status and result.row:
                return render_template("card_view.html", data=result.row)
        except Exception as e:
            print(f"Error fetching record {e}")
            flash("Error finding item","danger")
    return redirect(url_for("cards.list"))

@cards.route("/delete", methods=["GET"])
@admin_permission.require(http_exception=403)
def delete():
    id = request.args.get("id")
    if not id:
        flash("Missing id", "danger")
    else:
        args = {**request.args}
        del args["id"]
        result = DB.delete("DELETE FROM IS601_Quick_Cards WHERE id = %s", id)
        if result.status:
            flash("Successfully deleted item", "success")
    return redirect(url_for("cards.list", **args))

@cards.route("/list", methods=["GET"])
def list():
    form = CardSearchForm(request.args)
    allowed_columns = ["name", "text", "mana_cost", "rarity", "card_class", "card_type", "spell_school"]
    form.sort.choices = [(k, k) for k in allowed_columns]
    query = """
    SELECT id, name, text, flavor_text, mana_cost, rarity, card_class, card_type, card_set,spell_school, 
    IFNULL((SElECT count(1) FROM IS601_Quick_WatchList WHERE user_id = %(user_id)s and card_id = IS601_Quick_Cards.id), 0) as 'is_assoc' 
    FROM IS601_Quick_Cards
     WHERE 1=1
    """
    args = {"user_id":current_user.id}
    where = ""
    if form.name.data:
        args["name"] = f"%{form.name.data}%"
        where += " AND name LIKE %(name)s"
    if form.text.data:
        args["text"] = f"%{form.text.data}%"
        where += " AND text LIKE %(text)s"
    if form.mana_cost.data:
        args["mana"] = form.mana_cost.data
        where += " AND mana_cost = %(mana)s"
    if form.rarity.data:
        args["rarity"] = form.rarity.data
        where += " AND rarity = %(rarity)s"
    if form.card_class.data:
        args["card_class"] = form.card_class.data
        where += " AND card_class = %(card_class)s"
    if form.card_type.data:
        args["card_type"] = form.card_type.data
        where += " AND card_type = %(card_type)s"
    if form.card_type.data:
        args["card_type"] = form.card_type.data
        where += " AND card_type = %(card_type)s"
    if form.spell_school.data:
        args["spell_school"] = form.spell_school.data
        where += " AND spell_school = %(spell_school)s"
    if form.sort.data in allowed_columns and form.order.data in ["asc", "desc"]:
        where += f" ORDER BY {form.sort.data} {form.order.data}"
    
    
    limit = 10
    if form.limit.data:
        limit = form.limit.data
        if limit < 1:
            limit = 1
        if limit > 100:
            limit = 100
        args["limit"] = limit
        where += " LIMIT %(limit)s"
    result = DB.selectAll(query+where, args)
    rows = []
    if result.status and result.rows:
        rows = result.rows
    total_records = get_total(""" IS601_Quick_Cards""")
    return render_template("card_list.html", rows=rows, form=form, total_records=total_records)

@cards.route("/track", methods=["GET"])
@login_required
def track():

    id = request.args.get("id")
    args = {**request.args}
    del args["id"]
    if not id:
        flash("Missing id parameter", "danger")
    else:
        params = {"user_id": current_user.id, "card_id": id}
        try:
            try:
                result = DB.insertOne("INSERT INTO IS601_Quick_WatchList (card_id, user_id) VALUES (%(card_id)s, %(user_id)s)", params)
                if result.status:
                    flash("Added card to your watch list", "success")
            except Exception as e:
                print(f"Should just be a duplicate exception and can be ignored {e}")
                result = DB.delete("DELETE FROM IS601_Quick_WatchList WHERE card_id = %(card_id)s AND user_id = %(user_id)s", params)
                if result.status:
                    flash("Removed card from your watch list", "success")
        except Exception as e:
            print(f"Error doing something with track/untrack {e}")
            flash("An unhandled error occurred please try again" ,"danger")
        
    url = request.referrer
    if url:
        from urllib.parse import urlparse
        url_stuff = urlparse(url)
        watchlist_url = url_for("cards.watchlist")
        print(f"Parsed url {url_stuff} {watchlist_url}")
        if url_stuff.path == url_for("cards.watchlist"):
            return redirect(url_for("cards.watchlist", **args))
        elif url_stuff.path == url_for("cards.view"):
            args["id"] = id
            return redirect(url_for("cards.view", **args))
    return redirect(url_for("cards.list", **args))

@cards.route("/watchlist", methods=["GET"])
def watchlist():
    
    id = request.args.get("id", current_user.id)
    form = CardSearchForm(request.args)
    allowed_columns = ["name", "text", "mana_cost", "rarity", "card_class", "card_type", "spell_school"]
    form.sort.choices = [(k, k) for k in allowed_columns]
    query = """
    SELECT c.id, name, text, flavor_text, mana_cost, rarity, card_class, card_type, card_set,spell_school, 1 as 'is_assoc' 
    FROM IS601_Quick_Cards c JOIN IS601_Quick_WatchList w ON c.id = w.card_id
    
     WHERE w.user_id = %(user_id)s
    """
    args = {"user_id":id}
    where = ""
    if form.name.data:
        args["name"] = f"%{form.name.data}%"
        where += " AND name LIKE %(name)s"
    if form.text.data:
        args["text"] = f"%{form.text.data}%"
        where += " AND text LIKE %(text)s"
    if form.mana_cost.data:
        args["mana"] = form.mana_cost.data
        where += " AND mana_cost = %(mana)s"
    if form.rarity.data:
        args["rarity"] = form.rarity.data
        where += " AND rarity = %(rarity)s"
    if form.card_class.data:
        args["card_class"] = form.card_class.data
        where += " AND card_class = %(card_class)s"
    if form.card_type.data:
        args["card_type"] = form.card_type.data
        where += " AND card_type = %(card_type)s"
    if form.card_type.data:
        args["card_type"] = form.card_type.data
        where += " AND card_type = %(card_type)s"
    if form.spell_school.data:
        args["spell_school"] = form.spell_school.data
        where += " AND spell_school = %(spell_school)s"
    if form.sort.data in allowed_columns and form.order.data in ["asc", "desc"]:
        where += f" ORDER BY {form.sort.data} {form.order.data}"
    
    
    limit = 10
    if form.limit.data:
        limit = form.limit.data
        if limit < 1:
            limit = 1
        if limit > 100:
            limit = 100
        args["limit"] = limit
        where += " LIMIT %(limit)s"
    result = DB.selectAll(query+where, args)
    rows = []
    if result.status and result.rows:
        rows = result.rows

    total_records = get_total(""" IS601_Quick_Cards c JOIN IS601_Quick_WatchList w ON c.id = w.card_id
     WHERE w.user_id = %(user_id)s""", {"user_id": id})
    return render_template("card_list.html", rows=rows, form=form, title="Watchlist", total_records=total_records)

@cards.route("/clear", methods=["GET"])
def clear():
    id = request.args.get("id")
    args = {**request.args}
    if "id" in args:
        del args["id"]
    if not id:
        flash("Missing id", "danger")
    else:
        if id == current_user.id or current_user.has_role("Admin"):
            try:
                result = DB.delete("DELETE FROM IS601_Quick_WatchList WHERE user_id = %(user_id)s", {"user_id":id})
                if result.status:
                    flash("Cleared watchlist", "success")
            except Exception as e:
                print(f"Error clearing watchlist {e}")
                flash("Error clearing watchlist","danger");
        

    return redirect(url_for("cards.watchlist", **args))

@cards.route("/associations", methods=["GET"])
@admin_permission.require(http_exception=403)
def associations():
    
    form = AdminCardSearchForm(request.args)
    allowed_columns = ["name", "text", "mana_cost", "rarity", "card_class", "card_type", "spell_school"]
    form.sort.choices = [(k, k) for k in allowed_columns]
    query = """
    SELECT u.id as user_id, username, c.id, name, text, flavor_text, mana_cost, rarity, card_class, card_type, card_set,spell_school
    FROM IS601_Quick_Cards c JOIN IS601_Quick_WatchList w ON c.id = w.card_id LEFT JOIN IS601_Users u on u.id = w.user_id
    
     WHERE 1=1
    """
    args = {}
    where = ""
    if form.username.data:
        args["username"] = f"%{form.username.data}%"
        where += " AND username LIKE %(username)s"
    if form.name.data:
        args["name"] = f"%{form.name.data}%"
        where += " AND name LIKE %(name)s"
    if form.text.data:
        args["text"] = f"%{form.text.data}%"
        where += " AND text LIKE %(text)s"
    if form.mana_cost.data:
        args["mana"] = form.mana_cost.data
        where += " AND mana_cost = %(mana)s"
    if form.rarity.data:
        args["rarity"] = form.rarity.data
        where += " AND rarity = %(rarity)s"
    if form.card_class.data:
        args["card_class"] = form.card_class.data
        where += " AND card_class = %(card_class)s"
    if form.card_type.data:
        args["card_type"] = form.card_type.data
        where += " AND card_type = %(card_type)s"
    if form.card_type.data:
        args["card_type"] = form.card_type.data
        where += " AND card_type = %(card_type)s"
    if form.spell_school.data:
        args["spell_school"] = form.spell_school.data
        where += " AND spell_school = %(spell_school)s"
    if form.sort.data in allowed_columns and form.order.data in ["asc", "desc"]:
        where += f" ORDER BY {form.sort.data} {form.order.data}"
    
    
    limit = 10
    if form.limit.data:
        limit = form.limit.data
        if limit < 1:
            limit = 1
        if limit > 100:
            limit = 100
        args["limit"] = limit
        where += " LIMIT %(limit)s"
    result = DB.selectAll(query+where, args)
    rows = []
    if result.status and result.rows:
        rows = result.rows

    total_records = get_total(""" IS601_Quick_Cards c JOIN IS601_Quick_WatchList w ON c.id = w.card_id""",)
    return render_template("card_list.html", rows=rows, form=form, title="Associations", total_records=total_records)

@cards.route("/unwatched", methods=["GET"])
@login_required
def unwatched():
    form = CardSearchForm(request.args)
    allowed_columns = ["name", "text", "mana_cost", "rarity", "card_class", "card_type", "spell_school"]
    form.sort.choices = [(k, k) for k in allowed_columns]
    query = """
    SELECT c.id, name, text, flavor_text, mana_cost, rarity, card_class, card_type, card_set,spell_school,
    IFNULL((SElECT count(1) FROM IS601_Quick_WatchList WHERE user_id = %(user_id)s and card_id = c.id), 0) as 'is_assoc' 
    FROM IS601_Quick_Cards c 
    
     WHERE c.id not in (SELECT DISTINCT card_id FROM IS601_Quick_WatchList)
    """
    args = {"user_id": current_user.id}
    where = ""
    if form.name.data:
        args["name"] = f"%{form.name.data}%"
        where += " AND name LIKE %(name)s"
    if form.text.data:
        args["text"] = f"%{form.text.data}%"
        where += " AND text LIKE %(text)s"
    if form.mana_cost.data:
        args["mana"] = form.mana_cost.data
        where += " AND mana_cost = %(mana)s"
    if form.rarity.data:
        args["rarity"] = form.rarity.data
        where += " AND rarity = %(rarity)s"
    if form.card_class.data:
        args["card_class"] = form.card_class.data
        where += " AND card_class = %(card_class)s"
    if form.card_type.data:
        args["card_type"] = form.card_type.data
        where += " AND card_type = %(card_type)s"
    if form.card_type.data:
        args["card_type"] = form.card_type.data
        where += " AND card_type = %(card_type)s"
    if form.spell_school.data:
        args["spell_school"] = form.spell_school.data
        where += " AND spell_school = %(spell_school)s"
    if form.sort.data in allowed_columns and form.order.data in ["asc", "desc"]:
        where += f" ORDER BY {form.sort.data} {form.order.data}"
    
    
    limit = 10
    if form.limit.data:
        limit = form.limit.data
        if limit < 1:
            limit = 1
        if limit > 100:
            limit = 100
        args["limit"] = limit
        where += " LIMIT %(limit)s"
    result = DB.selectAll(query+where, args)
    rows = []
    if result.status and result.rows:
        rows = result.rows

    total_records = get_total(""" IS601_Quick_Cards c 
     WHERE c.id not in (SELECT DISTINCT card_id FROM IS601_Quick_WatchList)""")
    return render_template("card_list.html", rows=rows, form=form, title="Unwatched Items", total_records=total_records)

@cards.route("/manage", methods=["GET"])
def manage():
    form = AssocForm(request.args)
    users = []
    cards = []
    username = form.username.data
    card_name = form.card.data
    if username and card_name:
        result = DB.selectAll("SELECT id, username FROM IS601_Users WHERE username like %(username)s LIMIT 25",{"username":f"%{username}%"})
        if result.status and result.rows:
            users = result.rows
        result = DB.selectAll("SELECT id, name FROM IS601_Quick_Cards WHERE name like %(card)s LIMIT 25", {"card":f"%{card_name}%"})
        if result.status and result.rows:
            cards = result.rows
    print(f"Users {users}")
    print(f"Cards {cards}")
    return render_template("card_association.html", users=users, cards=cards, form=form)

@cards.route("/manage_assoc", methods=["POST"])
def manage_assoc():
    users = request.form.getlist("users[]")
    cards = request.form.getlist("cards[]")
    print(users, cards)
    args = {**request.args}
    if users and cards: # we need both for this to work
        mappings = []
        for user in users:
            for card in cards:
                mappings.append({"user_id":user, "card_id":card})
        if len(mappings) > 0:
            for mapping in mappings:
                print(f"mapping {mapping}")
                try:
                    result = DB.insertOne("INSERT INTO IS601_Quick_WatchList (user_id, card_id) VALUES(%(user_id)s, %(card_id)s)", mapping)
                    if result.status:
                        pass
                        #flash(f"Successfully enabled/disabled roles for the user/role {len(mappings)} mappings", "success")
                except Exception as e:
                    print(f"Insert error {e}")
                    result = DB.delete("DELETE FROM IS601_Quick_WatchList WHERE user_id = %(user_id)s and card_id = %(card_id)s",mapping)
            flash("Successfully applied mappings", "success")
        else:
            flash("No user/card mappings", "danger")

    if "users" in args:
        del args["users"]
    if "cards" in args:
        del args["cards"]
    return redirect(url_for("cards.manage", **args))