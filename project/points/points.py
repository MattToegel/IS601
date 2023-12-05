from flask import Blueprint, flash, render_template,session
from flask_login import current_user

from points.forms import ChangePointsForm
from sql.db import DB 
from roles.permissions import admin_permission

points = Blueprint('points', __name__, url_prefix='/points', template_folder='templates')


def change_points(user_id, amount):
    # The COALESCE function is used to handle the case where there are no existing records for the user, ensuring that it defaults to 0 rather than NULL.
    result = DB.insertOne(
    """INSERT INTO IS601_Point_History (user_id, points_change, expected_total)
       SELECT %(user_id)s, %(amount)s, 
              COALESCE((SELECT SUM(points_change) 
                        FROM (SELECT points_change 
                              FROM IS601_Point_History 
                              WHERE user_id = %(user_id)s) AS sub), 0) + %(amount)s""",
            {"user_id": user_id, "amount": amount}
        )
    if result.status:
        DB.update("UPDATE IS601_Users set points = (SELECT SUM(IFNULL(points_change, 0)) FROM IS601_Point_History WHERE user_id = %(user_id)s) where id = %(user_id)s", {
            "user_id": user_id
        })
        if current_user.id == user_id:
            current_user.change_points(amount)
            session["user"] = current_user.toJson()
        return True
    return False
@points.route("/add", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def add():
    pointsForm = ChangePointsForm()
    if pointsForm.validate_on_submit():
        if pointsForm.amount.data != 0:
            result = DB.selectOne("SELECT id FROM IS601_Users where username = %s", pointsForm.username.data)
            if result.status and result.row:
                user_id = result.row["id"]
                status = change_points(user_id, pointsForm.amount.data)
                if status:
                    flash(f"Successfully gave {pointsForm.username.data} {pointsForm.amount.data} points", "success")
            else:
                flash(f"Could not find user with username {pointsForm.username.data}", "warning")
        else:
            flash("Amount must be a non-zero value", "warning")
    else:
        print("Form Errors:", pointsForm.errors)
    return render_template("add_points.html", form=pointsForm)