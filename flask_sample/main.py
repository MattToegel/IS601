# from https://towardsdatascience.com/deploy-to-google-cloud-run-using-github-actions-590ecf957af0
import os
import sys
from flask import Flask
from dotenv import load_dotenv
load_dotenv()
import flask_login
# added so modules can be found between the two different lookup states:
# from tests and from regular running of the app
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURR_DIR)
sys.path.append(CURR_DIR)

login_manager = flask_login.LoginManager()
# app = Flask(__name__)
def create_app(config_filename=''):
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "missing_secret")
    login_manager.init_app(app)
    # app.config.from_pyfile(config_filename)
    with app.app_context():
        from views.hello import hello
        app.register_blueprint(hello)
        from views.sample import sample
        app.register_blueprint(sample)
        from auth.auth import auth
        app.register_blueprint(auth)

        @login_manager.user_loader
        def load_user(user_id):
            from sql.db import DB
            from auth.models import User
            try:
                print("login_manager loading user")
                result = DB.selectOne("SELECT id, email FROM IS601_Users WHERE id = %s", user_id)
                if result.status:
                    return User(**result.row)
            except Exception as e:
                print(e)
            return None
        # DON'T DELETE, this cleans up the DB connection after each request
        # this avoids sleeping queries
        @app.teardown_request 
        def after_request_cleanup(ctx):
            from sql.db import DB
            DB.close()
        return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
