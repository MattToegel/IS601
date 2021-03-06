import functools

from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def admin_only(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        if current_user and current_user.is_authenticated and current_user.is_admin():
            return f(*args, **kwargs)
        else:
            flash("Admin only")
            return redirect(url_for('core.index'))
    return wrap


def create_app():
    print('created app')
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'this_is_mine'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    register_extensions(app)
    register_blueprints(app)
    setup_database(app)

    return app


def register_extensions(app):
    print("registering extensions")
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    # blueprint for auth routes in our app
    from land.models import Land
    from auth.models import Permission, User
    from core.models import Purchase, PurchaseType

    from resources.models import ResourceNode, InventoryToResource, Inventory, OreType, ResourceType, IngotType
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    from auth.auth import auth_bp
    from core.core import core_bp
    from land.land import land_bp
    from resources.resources import resources_bp
    app.register_blueprint(auth_bp)
    # blueprint for non-auth parts of app
    app.register_blueprint(core_bp)
    app.register_blueprint(land_bp, url_prefix='/land')
    app.register_blueprint(resources_bp, url_prefix='/resource')


def setup_database(app):
    with app.app_context():

        db.create_all()
        _admins = ('matt@test.com',)
        print("init db, setting up admins")
        from auth.models import User, Permission
        users = User.query.filter(User.email.in_(_admins)).all()
        for user in users:
            print('updating user')
            user.permission = Permission.ADMIN
            if user.get_coins() == 0:
                user.inventory.update_coins(100)
                print('updating coins')
            # user.active = True
        db.session.commit()


if __name__ == "__main__":
    # app.run(ssl_context=('cert.pem', 'key.pem'))
    print("Running")
    app = create_app()
    setup_database(app)
    #app.run(debug=True)


