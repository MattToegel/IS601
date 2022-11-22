from flask import Blueprint, render_template, flash, redirect, url_for, current_app
import math
from game.forms import GameForm
from sql.db import DB

from flask_login import login_required, current_user
game = Blueprint('game', __name__, url_prefix='/',template_folder='templates')

@game.route("/game", methods=["GET"])
@login_required
def play():
    form = GameForm()
    return render_template("game.html", form=form)

@game.route("/save", methods=["POST"])
@login_required
def save():
    form = GameForm()
    if form.validate_on_submit():
        # arcade project just needs the  below two
        user_id = current_user.get_id()
        score = int(form.score.data)
        # my game specifics
        hits = int(form.hits.data)
        defeated = int(form.defeated.data)
        spawned = int(form.spawned.data)
        ratio = float(form.ratio.data)
        # validate (TODO self: make sure it matches the JS side)
        penalty = hits * 0.25
        server_ratio = defeated/spawned
        points = defeated * 0.15 * server_ratio
        server_score = math.ceil(points - penalty)
        print("inc score", score, "server score", server_score)
        # arcade project isn't required to do any special validation
        if server_score == score: # should be valid
            # TODO validate other data for score integrity (best guess)
            try:
                # arcade project just needs to insert user_id and score
                result = DB.insertOne("""
                INSERT INTO IS601_S_Scores 
                (user_id, score, hits, defeated, spawned, ratio)
                VALUES (%s, %s, %s, %s, %s, %s)
                                      """,
                user_id, server_score, hits, defeated, spawned, round(server_ratio,2))
                if result.status:
                    print(f"score {score}")
                    flash(f"Saved score: {score}", "success")
                    if server_score > 0 and current_user.account.id > 0:
                        # math constants for scaling effects
                        x = 2
                        y = 1.5
                        points = math.ceil(pow(server_score / x, y))
                        if current_user.account.add_points(
                            change=points,
                            reason="game",
                            details=f"Recevied {points} points for a score of {server_score}"
                        ):
                            flash(f"You got {points} points!","success")
            except Exception as e:
                print("Error saving score", e)
                flash("There was a problem saving the score", "danger")
      
        
    return redirect(url_for('game.play'))

@game.route("/scores", methods=["GET"])
@current_app.cache.cached(timeout=30) # cache for 30 seconds since this is expensive
def scores():
    all_time_rows = []
    today_rows = []
    week_rows = []
    month_rows = []
    base_query = """
    SELECT username, score, hits, defeated, spawned, ratio, s.created, user_id
        FROM IS601_S_Scores s JOIN IS601_Users u on u.id = s.user_id
    """
    end_query = " ORDER BY s.score desc, s.created desc LIMIT 10"
    try:
        # all time
        query = base_query + end_query
        result = DB.selectAll(query,)
        if result.status and result.rows:
            all_time_rows = result.rows # [Score(**r) for r in result.rows]
    except Exception as e:
        print("Error getting all time scores", e)
        flash("Error getting all time scores", "danger")
    try:
        #  today
        date_query = """
        WHERE s.created >= addtime(CURDATE(), '00:00:00') 
        AND s.created <= addtime(CURDATE(), '23:59:59')
        """
        query = f"{base_query} {date_query} {end_query}"
        print("today", query)
        result = DB.selectAll(query,)
        if result.status and result.rows:
            today_rows = result.rows # [Score(**r) for r in result.rows]
    except Exception as e:
        print("Error getting day scores", e)
        flash("Error getting day scores", "danger")
    try:
        #  week
        date_query = """
       WHERE 
        s.created >= addtime(date_add(curdate(), interval  -WEEKDAY(curdate()) day), '00:00:00')
        AND
        s.created <= addtime(date_add(date_add(curdate(), interval  -WEEKDAY(curdate())-1 day), interval 7 day), '23:59:59')
       
        """
        query = f"{base_query} {date_query} {end_query}"
        print("week", query)
        result = DB.selectAll(query,)
        if result.status and result.rows:
            week_rows = result.rows # [Score(**r) for r in result.rows]
    except Exception as e:
        print("Error getting week scores", e)
        flash("Error getting week scores", "danger")
    try:
        #  month
        date_query = """
       WHERE 
        s.created >=  addtime(dATE_SUB(curdate(),INTERVAL DAYOFMONTH(curdate())-1 DAY), '00:00:00')
        AND
        s.created <= addtime(LAST_DAY(CURDATE()), '23:59:59')
        """
        query = f"{base_query} {date_query} {end_query}"
        print("month", query)
        result = DB.selectAll(query,)
       
        if result.status and result.rows:
            month_rows = result.rows # [Score(**r) for r in result.rows]
    except Exception as e:
        print("Error getting month scores", e)
        flash("Error getting month scores", "danger")
    return render_template("scoreboard.html", all_rows=all_time_rows,day_rows=today_rows, week_rows=week_rows,month_rows=month_rows )

@game.route("/")
def index():
    return render_template("index.html")