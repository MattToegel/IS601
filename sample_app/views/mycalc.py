from flask import Blueprint, request, render_template
import calc.MyCalc

c = calc.MyCalc.AdvMyCalc()  # here the state is persisted between requests (note it may be shared across users)
mycalc = Blueprint('mycalc', __name__, url_prefix='/mycalc')


@mycalc.route('/', methods=['GET'])
def view_calc():
    return render_template("my_calc.html")


@mycalc.route('/', methods=['POST'])
def do_calc():
    # c = calc.MyCalc.AdvMyCalc() # here the state resets each time
    checks = calc.MyCalc.AdvMyCalc.ops
    data = request.form
    iSTR = data.get("eq")
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
            return render_template("my_calc.html", result=r, eq=iSTR)
    print("The action you tried is not supported, please try again")
    return render_template("my_calc.html", result="UNSUPPORTED", eq=iSTR)
