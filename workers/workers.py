from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from workers.models import Worker
workers_bp = Blueprint('workers', __name__, template_folder='templates')


@workers_bp.route('/gather/<int:resource_id>')
def pick_to_gather(resource_id):
    workers = Worker.query.filter_by(user_id=current_user.id).order_by(Worker.health.desc(), Worker.next_action.asc()).all()
    return render_template("workers.html", resource_id=resource_id, workers=workers)


@workers_bp.route('/hire')
@login_required
def hire_random():
    # TODO add a cost
    worker = Worker()
    worker.generate(current_user.id)
    flash('Congrats you hired ' + worker.name)
    return redirect(url_for('workers.my_workers'))


@workers_bp.route('/crew')
@login_required
def my_workers():
    print('current user: ' + str(current_user.id))
    workers = Worker.query.filter_by(user_id=current_user.id).all()
    print('results: ' + str(len(workers)))
    return render_template("workers.html", workers=workers)
