from flask import Blueprint, request, render_template, flash
import calc.MyCalc
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from sample_app.base_model import db
from sample_app.calc.models import SimpleHistory

c = calc.MyCalc.AdvMyCalc()  # here the state is persisted between requests (note it may be shared across users)
mycalc = Blueprint('mycalc', __name__, url_prefix='/mycalc')


@mycalc.route('/', methods=['GET', 'POST'])
def do_calc():
    # c = calc.MyCalc.AdvMyCalc() # here the state resets each time

    data = request.form
    iSTR = data.get("eq")
    if iSTR is not None:
        checks = calc.MyCalc.AdvMyCalc.ops
        for check in checks:
            if check in iSTR:
                nums = iSTR.split(check)
                if nums[0] == '':
                    nums[0] = "ans"
                try:
                    r = c.calc(nums[0].strip(), check, nums[1].strip())

                    print("R is " + str(r))
                except:
                    r = "ERROR"
                if not current_user.is_anonymous:
                    sh = SimpleHistory(eq=iSTR,result=r,user_id=current_user.id)
                    db.session.add(sh)
                    try:
                        db.session.commit()
                        flash("Saved history")
                    except SQLAlchemyError as e:
                        print(e)
                        flash(str(e))
                        db.session.rollback()

                return render_template("my_calc.html", result=r, eq=iSTR)
        print("The action you tried is not supported, please try again")
        return render_template("my_calc.html", result="UNSUPPORTED", eq=iSTR)
    return render_template("my_calc.html")
