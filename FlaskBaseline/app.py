import functools

from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'users.login'


def has_role(role):
    def decorator(f):
        @functools.wraps(f)
        def wrap(*args, **kwargs):
            if current_user and current_user.is_authenticated and current_user.has_role(role):
                return f(*args, **kwargs)
            else:
                flash("You lack the proper role for this")
                return redirect(url_for('users.login'))
        return wrap
    return decorator


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'this_is_mine'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    register_extensions(app)
    register_blueprints(app)
    setup_database(app)

    return app


def register_extensions(app):
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    from users.users import users_bp
    app.register_blueprint(users_bp)

    from users.models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))


def setup_database(app):
    with app.app_context():
        from users.models import User
        from users.models import RolesUsers
        from users.models import Role
        db.create_all()

        # TODO setup admin
        role = Role()
        role.name = "Admin"
        role.description = "This is the admin role"
        db.session.add(role)
        try:
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            if "UNIQUE constraint" in str(err):
                print("Admin role already exists, this is ok")
            else:
                print("Error with admin role, this needs to be looked into")
        role = Role()
        role.name = "Generic"
        role.description = "Just a viewer of the site"
        db.session.add(role)
        try:
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()

        # TODO find admin user
        user = User.query.filter_by(email="matt@test.com").first()
        if user is not None:
            if not user.has_role("Admin"):
                role = Role.query.filter_by(name="Admin").first()
                user.roles.append(role)
                try:
                    db.session.commit()
                except IntegrityError as err:
                    db.session.rollback()
                    if "UNIQUE constraint" in str(err):
                        print("Admin relationship duplicate constraint issue")
                    else:
                        print("Error with user-role relationship")
                print("Added admin role")
            else:
                print("Admin is already admin")


if __name__ == '__main__':
    app = create_app()
    app.run()
