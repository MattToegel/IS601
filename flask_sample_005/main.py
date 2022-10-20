# from https://towardsdatascience.com/deploy-to-google-cloud-run-using-github-actions-590ecf957af0
import os
import sys
from flask import Flask

# added so modules can be found between the two different lookup states:
# from tests and from regular running of the app
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURR_DIR)
sys.path.append(CURR_DIR)


# app = Flask(__name__)
def create_app(config_filename=''):
    app = Flask(__name__)
    # app.config.from_pyfile(config_filename)
    with app.app_context():
        from views.hello import hello
        app.register_blueprint(hello)
        return app


app = create_app()
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))