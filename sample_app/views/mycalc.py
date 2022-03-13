from flask import Blueprint, request, render_template
import calc.MyCalc

mycalc = Blueprint('mycalc', __name__, url_prefix='/mycalc')

@mycalc.route('/', methods=['GET'])
def view_calc():
    return render_template("my_calc.html", result="")

@mycalc.route('/', methods=['POST'])
def do_calc():
    c = calc.MyCalc.AdvMyCalc()
    checks = calc.MyCalc.AdvMyCalc.ops
    handled = False
    data = request.form
    iSTR = data.get("eq")
    for check in checks:
        if not handled and check in iSTR:
            nums = iSTR.split(check)
            try:
                r = c.calc(nums[0].strip(), check, nums[1].strip())

                print("R is " + str(r))
            except:
                r = ""
            handled = True
            return render_template("my_calc.html", result=r)
    if not handled:
        print("The action you tried is not supported, please try again")
    return render_template("my_calc.html", result="")
