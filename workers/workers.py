from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import and_

from app import admin_only, db
from auth.models import User
from core.forms import PurchaseForm
from core.models import Purchase, PurchaseType
from resources.resources import harvest
from workers.models import Worker, Promotion

workers_bp = Blueprint('workers', __name__, template_folder='templates')


@workers_bp.route('/gather/<int:resource_id>')
@workers_bp.route('/gather/<int:resource_id>/<int:worker_id>')
@login_required
def pick_to_gather(resource_id, worker_id=-1):
    if worker_id == -1:
        workers = Worker.query.filter(Worker.next_action <= datetime.utcnow())\
            .order_by(Worker.health, Worker.efficiency, Worker.skill).all()
        print(resource_id)
        return render_template("workers.html", workers=workers, gather=resource_id)
    else:
        worker = Worker.query.get(int(worker_id))
        if worker is not None:
            # good idea to check here in case someone memorizes the API endpoint
            # since it's just based on UI whether or not a worker can gather
            if worker.can_gather():
                # trigger cooldown
                worker.did_gather()
                # what did we get?
                result = harvest(resource_id, worker)
                n = result[1]
                res = result[0]
                if res is None:
                    msg = "resources"
                else:
                    msg = res.get_name()
                db.session.commit()
                if n > 0:
                    current_user.inventory.update_inventory(res.get_name(), n)
                    flash(worker.name + " gathered " + str(n) + " " + msg)
                else:
                    flash(worker.name + " failed to gather any resources")
            else:
                flash(worker.name + " is unable to gather any resources at this time.")
        else:
            flash("Worker wasn't found")
        return redirect(url_for('land.show_my_land'))


@workers_bp.route('/lfw/<int:page>')
@workers_bp.route('/lfw')
def looking_for_work(page=1):
    from auth.models import User
    user_id = User.get_sys_user_id
    workers = Worker.query.filter_by(user_id=user_id).paginate(page, 12, False)
    next_url = url_for('workers.looking_for_work', page=workers.next_num) \
        if workers.has_next else None
    prev_url = url_for('workers.looking_for_work', page=workers.prev_num) \
        if workers.has_prev else None
    return render_template("workers.html", workers=workers.items, prev_url=prev_url,
                           next_url=next_url, current_page=page, lfg=True)


@workers_bp.route('/fired')
@login_required
@admin_only
def get_fired_workers():
    from auth.models import User
    user_id = User.get_sys_user_id
    print('worker sys id ')
    print(user_id)
    workers = Worker.query.filter(and_(Worker.user_id==user_id, Worker.previous_user_id==user_id)).all()
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


@workers_bp.route('/hire/<int:worker_id>')
@login_required
def hire_specific(worker_id):
    worker = Worker.query.get(int(worker_id))
    sys_user_id = User.get_sys_user_id
    # make sure it's currently owned by the system user
    if worker is not None and worker.user_id == sys_user_id:
        cost = worker.get_promote_cost()
        balance = current_user.get_coins()
        if balance >= cost:
            # cache previous owner
            prev_user_id = worker.previous_user_id
            # make current owner previous owner
            worker.previous_user_id = worker.user_id
            # assign to current user
            worker.user_id = current_user.id
            # make purchase (created db object and commits if successful
            current_user.make_purchase(cost, PurchaseType.WORKER_LFG)
            if prev_user_id != sys_user_id:
                reward = int(cost * 0.5)
                # find previous user to give commission
                rewardee = User.query.get(int(prev_user_id))
                if rewardee is not None:
                    rewardee.receive_coins(reward)
                    # TODO add notification?
            db.session.commit()  # shouldn't be needed since make_purchase commits, but just to be safe
            flash('Congrats you hired ' + worker.name + " for " + str(cost) + " coins!")
    # assume unavailable if worker is none or not owned by sys user
    flash("Sorry, that worker is no longer available")
    return redirect(url_for('workers.looking_for_work'))


@workers_bp.route('/hire', methods=['GET', 'POST'])
@login_required
def hire_random():
    # TODO add a cost
    # we'll get balance/cost for both GET/POST (not gonna trust data from UI)
    cost = current_user.get_hire_cost()
    form = PurchaseForm()
    balance = current_user.get_coins()
    if form.validate_on_submit():
        if cost <= balance:
            worker = Worker()
            worker.generate(current_user.id)
            current_user.make_purchase(cost, PurchaseType.WORKER)
            db.session.commit()
            flash('Congrats you hired ' + worker.name + " for " + str(cost) + " coins!")
            return redirect(url_for('workers.hire_random'))
        else:
            flash("Sorry you can't afford to hire any more workers")

    form.cost.data = cost
    form.submit.label.text = "Hire"
    return render_template('hire_worker.html', form=form, balance=balance), 200


@workers_bp.route('/promote/<int:worker_id>')
@login_required
def promote_worker(worker_id):
    worker = Worker.query.get(int(worker_id))
    if worker is not None:
        print('attempting promote')
        promo_status = worker.promote()
        if promo_status is False:
            flash("Sorry, you can't afford to promote " + worker.name)
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


@workers_bp.route('/')
@workers_bp.route('/<int:page>')
@login_required
def my_workers(page=1):
    workers = Worker.query.filter_by(user_id=current_user.id).paginate(page, 12, False)
    next_url = url_for('workers.my_workers', page=workers.next_num) \
        if workers.has_next else None
    prev_url = url_for('workers.my_workers', page=workers.prev_num) \
        if workers.has_prev else None
    return render_template("workers.html", workers=workers.items, prev_url=prev_url,
                           next_url=next_url, current_page=page)


