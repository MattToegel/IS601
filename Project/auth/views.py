from flask import Blueprint, url_for, render_template, request, flash
from flask_login import login_required, logout_user, login_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import redirect

from .forms import RegistrationForm, LoginForm
from .models import User, db

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/home')
def home():
    return render_template('index.html')

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
            flash(str(e), "error")
            db.session.rollback()

    return render_template('registration.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for('auth.home'))
        flash('Invalid email address or Password.', "danger")
    return render_template('login.html', form=form)


@auth.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))


@auth.route("/forbidden", methods=['GET', 'POST'])
@login_required
def protected():
    return redirect(url_for('forbidden.html'))
