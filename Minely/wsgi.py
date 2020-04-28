from app import create_app, setup_database
#if __name__ == "__main__":
print('from wsgi')
app = create_app()
setup_database(app)
#app.run()
