from app import create_app, setup_database, db
from workers.models import Worker
"""used by manager.py for flask db migrate stuff"""
app = create_app()
db.init_app(app)
setup_database(app)