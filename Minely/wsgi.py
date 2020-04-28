
#if __name__ == "__main__":
from app import create_app, setup_database

print('from wsgi')
app = create_app()
setup_database(app)
#app.run()
