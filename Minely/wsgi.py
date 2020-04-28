
from app import create_app, setup_database
app = create_app()
setup_database(app)
app.run()