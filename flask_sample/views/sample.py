from flask import Blueprint, request, render_template

from sql.db import DB
sample = Blueprint('sample', __name__, url_prefix='/sample')


@sample.route('/add', methods=['GET','POST'])
def add():
    k = request.form.get("key", None)
    v = request.form.get("value", None)
    resp = None
    if k and v:
        try:
            result = DB.insertOne("INSERT INTO IS601_Sample (name, val) VALUES(%s, %s)", k, v)
            if result.status:
                resp = "Saved record"
        except Exception as e:
            resp = e
        

    return render_template("add_sample.html", resp=resp)
