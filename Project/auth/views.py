from flask import Blueprint, url_for, render_template, request, flash, session, current_app
from flask_login import login_required, logout_user, login_user, current_user
from flask_principal import identity_changed, AnonymousIdentity, Permission, RoleNeed, Identity

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import redirect

from .forms import RegistrationForm, LoginForm, ProfileForm
from .models import User, db
from helpers import handle_duplicate_column

auth = Blueprint('auth', __name__, template_folder='templates')

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('Admin'))

"""@auth.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404"""


@auth.errorhandler(403)
def permission_denied(e):
    print("denied")
    # note that we set the 404 status explicitly
    return render_template('permission_denied.html'), 403


@auth.route('/home')
def home():
    return render_template('index.html')


@auth.route("/admin")
@admin_permission.require(403)
def test_admin():
    return render_template("test_admin.html")


@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password1.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash("Successfully registered", "success")
            return redirect(url_for('auth.login'))
        except SQLAlchemyError as e:
            print(e)
            handle_duplicate_column(str(e.orig))
            db.session.rollback()

    return render_template('registration.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # login with username OR email
        user = User.query.filter(or_(User.email == form.email.data, User.username == form.email.data)).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next_route = request.args.get("next")
            # Tell Flask-Principal the identity changed
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.id))
            return redirect(next_route or url_for('auth.home'))
        flash('Invalid login details.', "danger")
    return render_template('login.html', form=form)


@auth.route("/logout")
# @login_required
def logout():
    logout_user()
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    return redirect(url_for('auth.home'))


@auth.route("/forbidden", methods=['GET', 'POST'])
@login_required
def protected():
    return redirect(url_for('forbidden.html'))


@auth.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        cpw = form.current_password.data
        pw = form.password1.data
        updating_password = False
        if len(pw) > 0 and len(cpw) > 0 and current_user.verify_password(cpw):
            current_user.set_password(pw)
            updating_password = True
        current_user.email = form.email.data
        current_user.username = form.username.data
        try:
            db.session.add(current_user)
            db.session.commit()
            flash("Saved Profile", "success")
            if updating_password:
                flash("Password Changed", "success")
        except SQLAlchemyError as e:
            print(e)
            handle_duplicate_column(str(e.orig))

    return render_template('profile.html', form=form)
