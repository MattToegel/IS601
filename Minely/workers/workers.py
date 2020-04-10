from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import admin_only
from workers.models import Worker, Promotion

workers_bp = Blueprint('workers', __name__, template_folder='templates')


@workers_bp.route('/gather/<int:resource_id>')
def pick_to_gather(resource_id):
    workers = Worker.query.filter_by(user_id=current_user.id).order_by(Worker.health.desc(), Worker.next_action.asc()).all()
    return render_template("workers.html", resource_id=resource_id, workers=workers)


@workers_bp.route('/fired')
@login_required
@admin_only
def get_fired_workers():
    from auth.models import User
    # find out system user if available
    sysuser = User.query.filter_by(name="System").first()
    sysuserid = -1
    if sysuser is not None:
        sysuserid = sysuser.id
    # find workers owned by our system user or user 1 (if system user wasn't found when worker was fired)
    workers = Worker.query.filter(or_(Worker.user_id==1, Worker.user_id==sysuserid)).all()
    return render_template("workers.html", workers=workers)


@workers_bp.route('/fire/<int:worker_id>')
@login_required
def fire(worker_id):
    worker = Worker.query.get(int(worker_id))
    if worker is not None:
        if worker.user_id == current_user.id:
            worker.fire()
            flash("You fired " + worker.name)
        else:
            flash("You can't fire a worker that isn't part of your crew.")
    else:
        flash("Couldn't find particular worker")
    return redirect(url_for('workers.my_workers'))


@workers_bp.route('/hire')
@login_required
def hire_random():
    # TODO add a cost
    worker = Worker()
    worker.generate(current_user.id)
    flash('Congrats you hired ' + worker.name)
    return redirect(url_for('workers.my_workers'))


@workers_bp.route('/promote/<int:worker_id>')
@login_required
def promote_worker(worker_id):
    worker = Worker.query.get(int(worker_id))
    if worker is not None:
        print('attempting promote')
        promo_status = worker.promote()
        if promo_status is False:
            flash("Sorry, you can't afford to promote " . worker.name)
        elif promo_status == Promotion.NONE:
            flash(worker.name + " is already at maximum skills.")
        elif promo_status == Promotion.INCREASED_SKILL:
            flash("Congrats " + worker.name + " increased their skill")
        elif promo_status == Promotion.INCREASED_EFFICIENCY:
            flash("Congrats " + worker.name + " increased their efficiency")
        elif promo_status == Promotion.MAXED_SKILL:
            flash("Congrats " + worker.name + " maxed their skill")
        elif promo_status == Promotion.MAXED_EFFICIENCY:
            flash("Congrats " + worker.name + " maxed their efficiency")
    return redirect(url_for('workers.my_workers'))


@workers_bp.route('/crew')
@login_required
def my_workers():
    print('current user: ' + str(current_user.id))
    workers = Worker.query.filter_by(user_id=current_user.id).all()
    print('results: ' + str(len(workers)))
    return render_template("workers.html", workers=workers)
