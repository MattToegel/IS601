from flask import Blueprint, render_template, flash, redirect, url_for,current_app, session
from auth.forms import LoginForm, ProfileForm, RegisterForm
from sql.db import DB

from flask_login import login_user, login_required, logout_user, current_user
from auth.models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

from flask_principal import Identity, AnonymousIdentity, \
     identity_changed

auth = Blueprint('auth', __name__, url_prefix='/',template_folder='templates')

def check_duplicate(e):

    import re
    r = re.match(".*IS601_Users.(\w+)", e.args[0].args[1])
    if r:
        flash(f"The chosen {r.group(1   )} is not available", "warning")
    else:
        flash("Unknown error occurred, please try again", "danger")
        print(e)

@auth.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    # wtform validators are both client-side and server-side
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        username = form.username.data
        try:
            hash = bcrypt.generate_password_hash(password)
            # save the hash, not the plaintext password
            result = DB.insertOne("INSERT INTO IS601_Users (email, username, password) VALUES (%s, %s, %s)", email, username, hash)
            if result.status:
                flash("Successfully registered","success")
        except Exception as e:
            check_duplicate(e)
    return render_template("register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        is_valid = True
        email = form.email.data # email or username
        password = form.password.data
        if is_valid:
            try:
                result = DB.selectOne("SELECT id, email, username, password FROM IS601_Users where email= %(email)s or username=%(email)s", {"email":email})
                if result.status and result.row:
                    hash = result.row["password"]
                    if bcrypt.check_password_hash(hash, password):
                        from roles.models import Role
                        del result.row["password"] # don't carry password/hash beyond here
                        user = User(**result.row)
                        # get roles
                        result = DB.selectAll("""
                        SELECT name FROM IS601_Roles r JOIN IS601_UserRoles ur on r.id = ur.role_id WHERE ur.user_id = %s AND r.is_active = 1 AND ur.is_active = 1
                        """, user.id)
                        if result.status and result.rows:
                            print("role rows", result.rows)
                            user.roles = [Role(**r) for r in result.rows]
                        print(f"Roles: {user.roles}")
                        success = login_user(user) # login the user via flask_login
                        
                        if success:
                            # Tell Flask-Principal the identity changed
                            identity_changed.send(current_app._get_current_object(),
                                    identity=Identity(user.id))
                            # store user object in session as json
                            session["user"] = user.toJson()
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
     # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    flash("Successfully logged out", "success")
    return redirect(url_for("auth.login"))

@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = current_user.get_id()
    form = ProfileForm()
    if form.validate_on_submit():
        is_valid = True
        email = form.email.data
        username = form.username.data
        current_password = form.current_password.data
        password = form.password.data
        confirm = form.confirm.data
        # handle password change only if all 3 are provided
        if current_password and password and confirm:
            try:
                result = DB.selectOne("SELECT password FROM IS601_Users where id = %s", user_id)
                if result.status and result.row:
                    # verify current password
                    if bcrypt.check_password_hash(result.row["password"], current_password):
                        # update new password
                        hash = bcrypt.generate_password_hash(password)
                        try:
                            result = DB.update("UPDATE IS601_Users SET password = %s WHERE id = %s", hash, user_id)
                            if result.status:
                                flash("Updated password", "success")
                        except Exception as ue:
                            flash(ue, "danger")
                    else:
                        flash("Invalid password","danger")
            except Exception as se:
                flash(se, "danger")
        
        if is_valid:
            try: # update email, username (this will trigger if nothing changed but it's fine)
                result = DB.update("UPDATE IS601_Users SET email = %s, username = %s WHERE id = %s", email, username, user_id)
                if result.status:
                    flash("Saved profile", "success")
            except Exception as e:
                check_duplicate(e)
    try:
        # get latest info if anything changed
        result = DB.selectOne("SELECT id, email, username FROM IS601_Users where id = %s", user_id)
        if result.status and result.row:
            user = User(**result.row)
            # switch how user is loaded so we don't lose error validations
            # form = ProfileForm(obj=user)
            print("loading user", user)
            form.username.data = user.username
            form.email.data = user.email
            # TODO update session
            current_user.email = user.email
            current_user.username = user.username
            session["user"] = current_user.toJson()
    except Exception as e:
        flash(e, "danger")
    return render_template("profile.html", form=form)