from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

from auth.forms import RegisterForm, LoginForm
from auth.models import User
from app import db
auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        # check if user actually exists
        # take the user supplied password, hash it, and compare it to the hashed password in database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))  # if user doesn't exist or password is wrong, reload the page
        if user.is_none():
            flash('Sorry this user account has been blocked')
            return redirect(url_for('auth.login'))
        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return redirect(url_for('core.profile'))
    return render_template('login.html', form=form)


@auth_bp.route('/signup', methods=['GET','POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        name = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        # if this returns a user, then the email already exists in database

        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@auth_bp.route('/user/<string:name>')
def get_user(name):
    print(name)
    user = User.query.filter_by(name=name).first()
    print(user.name)

    return jsonify(user=user.__dict__), 200

