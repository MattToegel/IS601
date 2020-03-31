from flask import Blueprint, jsonify, render_template

from land.models import Land, LandSchema
from server import db

land_bp = Blueprint('land', __name__, template_folder='templates')


@land_bp.route('/purchase/<int:user_id>')
def purchase(user_id):
    land = Land();
    land.user_id = user_id
    db.session.add(land)
    db.session.commit()

    return jsonify(id=land.id, user_id=land.user_id), 202


@land_bp.route('/myland/<int:user_id>')
def my_land(user_id):
    myland = Land.query.filter_by(user_id=user_id).all()
    ls = LandSchema(many=True)
    return jsonify(land=ls.dump(myland)), 200


@land_bp.route('/view/<int:user_id>')
def show_my_land(user_id):
    myland = Land.query.filter_by(user_id=user_id).all()
    return render_template('myland.html', my_land=myland);

