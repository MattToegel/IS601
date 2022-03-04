# from https://towardsdatascience.com/deploy-to-google-cloud-run-using-github-actions-590ecf957af0
import os

from flask import Flask


# app = Flask(__name__)
def create_app(config_filename=''):
    app = Flask(__name__)
    # app.config.from_pyfile(config_filename)
    from views.hello import hello
    app.register_blueprint(hello)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
