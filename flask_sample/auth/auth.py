from flask import Blueprint, render_template, flash, redirect, url_for
from auth.forms import LoginForm, RegisterForm
from sql.db import DB

from flask_login import login_user, login_required, logout_user
from auth.models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

auth = Blueprint('auth', __name__, url_prefix='/',template_folder='templates')


@auth.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    # wtform validators are both client-side and server-side
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            hash = bcrypt.generate_password_hash(password)
            # save the hash, not the plaintext password
            result = DB.insertOne("INSERT INTO IS601_Users (email, password) VALUES (%s, %s)", email, hash)
            if result.status:
                flash("Successfully registered","success")
        except Exception as e:
            flash(str(e), "danger")
    return render_template("register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            result = DB.selectOne("SELECT id, email, password FROM IS601_Users where email=%s", email)
            if result.status and result.row:
                hash = result.row["password"]
                if bcrypt.check_password_hash(hash, password):
                    del result.row["password"] # don't carry password/hash beyond here
                    user = User(**result.row)
                    success = login_user(user) # login the user via flask_login
                    if success:
                        flash("Log in successful", "success")
                        return redirect(url_for("auth.landing_page"))
                    else:
                        flash("Error logging in", "danger")
                else:
                    flash("Invalid password", "warning")
            else:
                # invalid user and invalid password together is too much info for a potential attacker
                # normally we return a single message for both "invalid username or password" so an attacker doens't know which part was correct
                flash("Invalid user", "warning")

        except Exception as e:
            flash(str(e), "danger")
    return render_template("login.html", form=form)

@auth.route("/landing-page", methods=["GET"])
@login_required
def landing_page():
    
    return render_template("landing_page.html")

@auth.route("/logout", methods=["GET"])
def logout():
    logout_user()
    flash("Successfully logged out", "success")
    return redirect(url_for("auth.login"))