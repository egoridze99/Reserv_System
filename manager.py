from app import app, db
from wsgi import *
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import Guest
import os
import re

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


# py manager.py get_telephones
@manager.command
def get_telephones():
    FILE_NAME = "telephones.txt"
    CURRENT_DIR = os.path.abspath(os.curdir)
    FILE_PATH = os.path.join(CURRENT_DIR, FILE_NAME)

    is_exist = os.path.exists(FILE_PATH)

    if is_exist:
        os.remove(FILE_PATH)

    with open(FILE_PATH, 'wt', encoding='utf-8') as f:
        phone_pattern = r'[\+]?[78][\-]?[\d]{3}[\-]?[\d]{3}[\-]?[\d]{2}[\-]?[\d]{2}'

        guests = Guest.query.all()
        for guest in guests:
            if re.fullmatch(phone_pattern, guest.telephone):
                f.write(f"{guest.telephone}\n")


if __name__ == '__main__':
    manager.run()
