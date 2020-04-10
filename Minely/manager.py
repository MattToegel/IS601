import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from setup import app, db
"""use this for flask db migrate, it replies on setup.py"""
app.config['SECRET_KEY'] = 'this_is_mine'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()