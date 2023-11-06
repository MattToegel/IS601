# from https://towardsdatascience.com/deploy-to-google-cloud-run-using-github-actions-590ecf957af0
import os
import sys
from flask import Flask
from dotenv import load_dotenv
load_dotenv()
from flask_caching import Cache
# added so modules can be found between the two different lookup states:
# from tests and from regular running of the app
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURR_DIR)
sys.path.append(CURR_DIR)

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

def create_app(config_filename=''):
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "missing_secret")
    
    cache.init_app(app)
    with app.app_context():
        from views.index import home
        app.register_blueprint(home)
        # given
        from views.geography import geo
        app.register_blueprint(geo)
        
        from views.admin import admin
        app.register_blueprint(admin)
        from views.organization import organization
        app.register_blueprint(organization)
        from views.donations import donations
        app.register_blueprint(donations)

        # an example of making a global function available in jinja templates
        # https://flask-caching.readthedocs.io/en/latest/
        @app.template_global()
        @cache.cached(timeout=30) # cache for 30 seconds since this is expensive
        def get_orgs():
            from sql.db import DB
            try:
                print("get organizations")
                # note this triggers for GET and POST
                result = DB.selectAll("SELECT distinct id, name FROM IS601_MP3_Organizations")
                if result.status:
                    return result.rows or []
            except Exception as e:
                print(e)
            return []
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