from flask import Blueprint, render_template, request, flash, jsonify

clientflash = Blueprint('flash', __name__)


@clientflash.route("/get_messages")
def get_messages():
    return render_template("flash.html")

@clientflash.route("/add_message", methods=["GET", "POST"])
def add_message():
    m = request.form.get("message")
    cat = request.form.get("category", "info")
    flash(m,cat)
    return jsonify({})
