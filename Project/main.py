# from https://towardsdatascience.com/deploy-to-google-cloud-run-using-github-actions-590ecf957af0
import os
import sys

from flask import Flask
from flask_login import LoginManager, current_user
from flask_principal import Principal, identity_loaded, UserNeed, RoleNeed

from sqlalchemy import MetaData



# added so modules can be found between the two different lookup states:
# from tests and from regular running of the app
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURR_DIR)
sys.path.append(CURR_DIR)

login_manager = LoginManager()


# app = Flask(__name__)
def create_app(config_filename=''):
    app = Flask(__name__)
    # add db connection
    # default to sqlite if DB_URL isn't setup properly
    db_url = os.environ.get("DB_URL", "sqlite:///mydb.db")
    if db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # configure flask-login
    # use an environment variable to pull the secret key
    # having this random each app start will clear the session every time the app reloads
    # set SECRET_KEY the same way you do DB_URL, just a different value
    SECRET_KEY = os.environ.get("SECRET_KEY", "thisisforlocal") # os.urandom(32 )
    app.config["SECRET_KEY"] = SECRET_KEY

    # app.config.from_pyfile(config_filename)
    register_blueprints(app)
    register_extensions(app)

    setup_db(app)
    return app


def register_extensions(app):
    print("registering extensions")
    from auth.models import db
    db.init_app(app)
    Principal(app) # https://pythonhosted.org/Flask-Principal/
    login_manager.init_app(app)


def setup_db(app):
    with app.app_context():
        print("create all")
        from auth.models import db
        db.create_all()
        db.session.commit()



def register_blueprints(app):
    from auth.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # Set the identity user object
        identity.user = current_user
        # Add the UserNeed to the identity
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        # Assuming the User model has a list of roles, update the
        # identity with the roles that the user provides
        if hasattr(current_user, 'roles'):
            print("User has roles {}".format(current_user.roles))
            for assoc in current_user.roles:
                if assoc.role is None:
                    continue
                print(assoc.role.name)
                identity.provides.add(RoleNeed(assoc.role.name))
        else:
            print("User doesn't have any roles")

    from views.hello import hello
    app.register_blueprint(hello)
    from auth.views import auth
    app.register_blueprint(auth)
    from admin.views import admin
    app.register_blueprint(admin)


if __name__ == "__main__":
    app = create_app()

    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8081)))
    from auth.models import db
    metadata = MetaData()
    metadata.reflect(bind=db.engine)
    # debugging output to verify tables were created
    for table in metadata.sorted_tables:
        print(table)

