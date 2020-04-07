import functools

from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_marshmallow import Marshmallow
# init SQLAlchemy so we can use it later in our models
from flask_wtf import CSRFProtect

app = Flask(__name__)

app.config['SECRET_KEY'] = 'this_is_mine'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
ma = Marshmallow(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    from auth.models import User
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


def admin_only(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        if current_user and current_user.is_authenticated and current_user.is_admin():
            return f(*args, **kwargs)
        else:
            flash("Admin only")
            return redirect(url_for('core.index'))
    return wrap

# db.create_all(app=create_app())
# blueprint for auth routes in our app
from auth.auth import auth_bp
app.register_blueprint(auth_bp)

# blueprint for non-auth parts of app
from core.core import core_bp
app.register_blueprint(core_bp)

from land.land import land_bp
app.register_blueprint(land_bp, url_prefix='/land')

from resources.resources import resources_bp
app.register_blueprint(resources_bp, url_prefix='/resource')


if __name__ == "__main__":
    # app.run(ssl_context=('cert.pem', 'key.pem'))
    app.run(debug=True)
