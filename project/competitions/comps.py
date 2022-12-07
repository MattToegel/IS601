from flask import Blueprint, render_template, flash, request, url_for, redirect
from accounts.models import Account
from competitions.forms import CompForm
from flask_login import login_required, current_user
comp = Blueprint('comp', __name__, url_prefix='/comp',template_folder='templates')
from sql.db import DB
@comp.route("/create", methods=["GET","POST"])
@login_required
def create():
    form = CompForm()
    current_user.get_id()
    if form.validate_on_submit():
        cost = int(form.starting_reward.data) + int(form.join_cost.data) + 1
        print("cost", cost)
        has_error = False
        if cost > current_user.get_balance():
            flash("You can't afford to create this competition", "warning")
            has_error = True
        if not current_user.account.remove_points(change=-cost, reason="create_comp", details=f"Paid {cost} to create comp {form.title.data}"):
            has_error = True
            flash("There was an error completing the transaction", "danger")
        if not has_error:
            try:
                result = DB.insertOne("""
                INSERT INTO IS601_S_Comps (title, min_participants, join_cost, payout_options,
                starting_reward, duration, min_score, creator_id)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                form.title.data,
                form.min_participants.data,
                form.join_cost.data,
                form.payout_options.data,
                form.starting_reward.data,
                form.duration.data,
                form.min_score.data,
                current_user.get_id())
                if result.status:
                    flash("Created competition", "success")
            except Exception as e:
                print("Error creating competition" ,e)
                flash("Error creating competition", "danger")
    return render_template("competition.html", form=form)

@comp.route("/list", methods=["GET","POST"])
@login_required
def list():
    rows = []
    try:
        result = DB.selectAll("""
        SELECT id, title, min_participants, current_participants, 
        join_cost, payout_options,current_reward, expires, min_score, creator_id,
        (select IF(count(1) > 0, 1, 0) FROM IS601_S_UserComps uc where uc.comp_id = c.id and uc.user_id = %s) as joined
        FROM IS601_S_Comps c ORDER BY expires LIMIT 25
        """, current_user.get_id())
        if result.status and result.rows:
            rows = result.rows
    except Exception as e:
        print("Error fetching competitions", e)
        flash("Error fetching cometitions", "danger")
    return render_template("competitions.html", rows=rows)

@comp.route("/join", methods=["GET"])
@login_required
def join():
    id = request.args.get("id")
    if not id:
        flash("Invalid competition", "danger")
        return redirect(url_for("comp.list"))
    try:
        DB.getDB().autocommit = False
        result = DB.selectOne("SELECT join_cost, title FROM IS601_S_Comps WHERE id = %s",id)
        if result.status and result.row:
            cost = int(result.row["join_cost"])
            title = result.row["title"]
            if cost > current_user.get_balance():
                flash("Can't afford to join", "danger")
            else:
                if(not current_user.account.remove_points(change=-cost, reason="join_comp", details=f"Joined {title} for {cost} credits")):
                    flash("Error performing transaction", "danger")
                else:
                    result = DB.insertOne("INSERT INTO IS601_S_UserComps (comp_id, user_id) VALUES (%s, %s)", id, current_user.get_id())
                    if result.status:
                        result = DB.update("""UPDATE IS601_S_Comps c set current_participants = 
                        (SELECT IFNULL(count(1), 0) FROM IS601_S_UserComps uc WHERE uc.comp_id = c.id),
                        current_reward = starting_reward + CEIL((SELECT IFNULL(count(1), 0) FROM IS601_S_UserComps uc WHERE uc.comp_id = c.id) * 0.5)
                        WHERE id = %s
                        """, id)
                        if result.status:
                            flash("Successfully joined competition" ,"success")
                            DB.getDB().commit()
                        else:
                            flash("Error updating competition stats", "danger")
                            DB.getDB().rollback()
                    else:
                        flash("Problem registering to competition", "danger")
                        DB.getDB().rollback()
    except Exception as e:
        print("Error joining competition" ,e)
        DB.getDB().rollback()
        flash("Error joining competition", "danger")
    return redirect(url_for("comp.list"))          


def get_comp_scores(id, limit = 10):
    scores = []
    try:
        # arcade project might be similar but without anything account related
        result = DB.selectAll("""
        SELECT * FROM (SELECT u.username, s.user_id, s.score,s.created, a.id as account_id, 
        DENSE_RANK() OVER (PARTITION BY s.user_id ORDER BY s.score desc) as `rank` FROM IS601_S_Scores s
    JOIN IS601_S_UserComps uc on uc.user_id = s.user_id
    JOIN IS601_S_Comps c on uc.comp_id = c.id
    JOIN IS601_S_Accounts a on a.user_id = s.user_id
    JOIN IS601_Users u on u.id = uc.user_id
    WHERE c.id = %s AND s.created BETWEEN uc.created AND c.expires
    )as t where `rank` = 1 ORDER BY score desc LIMIT %s
        """, id, limit)
        if result.status and result.rows:
            scores = result.rows
    except Exception as e:
        print("Error getting comp scores", e)
        flash("Error getting competition scores", "danger")
    return scores

@comp.route("/scores", methods=["GET"])
@login_required
def scores():
    id = request.args.get("id")
    if not id:
        flash("Invalid competition", "danger")
        return redirect(url_for("comp.list"))
    scores = get_comp_scores(id)
    return render_template("comp_scores.html", rows=scores)

def calc_winners():
    try:
        # find eligible expired comps (10 at a time)
        result = DB.selectAll("""SELECT c.id, c.title, c.payout_options, c.current_reward, c.min_score FROM IS601_S_Comps c
        WHERE expires <= CURRENT_TIMESTAMP() AND did_calc = 0 AND current_participants >= min_participants LIMIT 10
        """)
        if result.status and result.rows:
            print(f"Processing {len(result.rows)} competitions")
            import math
            
            for row in result.rows:
                po = row["payout_options"]
                reward = float(row["current_reward"])
                # convert each option to a float percentage, multiply by reward to get the values
                # ceil is used to round up so everyone gets at least 1 if applicable
                fpr,spr, tpr = [math.ceil(reward*(float(v)/100)) for v in po.split(",")]
                scores = get_comp_scores(row["id"], 3) # only need top 3
                at_least_one = False
                min_score = int(row["min_score"])
                # can definitely be improved, just a proof of concept
                if len(scores) >= 1 and int(scores[0]["score"]) >= min_score:
                    a = Account(id=scores[0]["account_id"])
                    a.add_points(change=fpr,reason="win_comp", details=f"Won 1st in competition {row['id']}")
                    print(f"Adding {fpr} points to account {a.id}")
                    at_least_one = True
                if len(scores) >= 2 and int(scores[1]["score"]) >= min_score:
                    a = Account(id=scores[1]["account_id"])
                    a.add_points(change=spr,reason="win_comp", details=f"Won 2nd in competition {row['id']}")
                    print(f"Adding {spr} points to account {a.id}")
                    at_least_one = True
                if len(scores) >= 3 and int(scores[2]["score"]) >= min_score:
                    a = Account(id=scores[2]["account_id"])
                    a.add_points(change=tpr,reason="win_comp", details=f"Won 3rd in competition {row['id']}")
                    print(f"Adding {tpr} points to account {a.id}")
                    at_least_one = True
                # expensive to do it this way
                # proper way is to aggregate ids and use an in() clause
                if at_least_one:
                    result = DB.update("UPDATE IS601_S_Comps set did_payout = 1, did_calc=1 WHERE id = %s", row['id'])
                    if result.status:
                        print(f"Paided out and closed comp {row['id']}")
                else:
                    result = DB.update("UPDATE IS601_S_Comps set did_calc=1 WHERE id = %s", row['id'])
                    print(f"Invalid comp; closed comp {row['id']}")
                DB.getDB().commit()
        else:
            print("No competitions to calculate")
    except Exception as e:
        print("Error calculating winners", e)
        DB.getDB().rollback()
