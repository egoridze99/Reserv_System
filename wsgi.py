from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import sys
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import Config

from domains import references_blueprint, reservations_blueprint, money_blueprint, certificate_blueprint, \
    queue_blueprint, base_blueprint, admin_blueprint, user_blueprint, customer_blueprint

from db import db
from domains.transactions import transactions_blueprint
from domains.webhook import webhook_blueprint
from scheduler_jobs import expired_queue_item_cleaner, expired_reservations_cleaner
from models import *
from sqlite_functions.get_shift_date import get_shift_date


def get_application_port():
    port = 5000

    try:
        port = sys.argv[1]
    except IndexError:
        print("Порт не задан. Используется порт по умолчанию")

    return port


def create_app():
    # CONFIGURING FLASK
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)
    CORS(flask_app)
    jwt = JWTManager(flask_app)

    db.init_app(flask_app)

    # CONFIGURING MIGRATIONS
    migrate = Migrate(flask_app, db, render_as_batch=True)
    manager = Manager(flask_app)
    manager.add_command('db', MigrateCommand)

    # MAPPING ROUTES
    flask_app.register_blueprint(base_blueprint, url_prefix='/api')
    flask_app.register_blueprint(references_blueprint, url_prefix='/api/reference')
    flask_app.register_blueprint(reservations_blueprint, url_prefix='/api/reservation')
    flask_app.register_blueprint(money_blueprint, url_prefix='/api/money')
    flask_app.register_blueprint(certificate_blueprint, url_prefix='/api/certificate')
    flask_app.register_blueprint(queue_blueprint, url_prefix='/api/queue')
    flask_app.register_blueprint(admin_blueprint, url_prefix='/api/admin')
    flask_app.register_blueprint(user_blueprint, url_prefix='/api/user')
    flask_app.register_blueprint(customer_blueprint, url_prefix='/api/customer')
    flask_app.register_blueprint(transactions_blueprint, url_prefix='/api/transactions')
    flask_app.register_blueprint(webhook_blueprint, url_prefix='/api/webhook')

    # CONFIGURING ADMIN PANEL
    admin_panel = Admin(flask_app, name='film_is_scheduler', template_mode='bootstrap3', url="/flask_admin_panel")
    admin_panel.add_view(ModelView(Cinema, db.session))
    admin_panel.add_view(ModelView(Room, db.session))
    admin_panel.add_view(ModelView(Guest, db.session))
    admin_panel.add_view(ModelView(Reservation, db.session))
    admin_panel.add_view(ModelView(User, db.session))
    admin_panel.add_view(ModelView(UpdateLogs, db.session))
    admin_panel.add_view(ModelView(Certificate, db.session))

    return flask_app


def configure_scheduler(app: 'Flask', db: 'SQLAlchemy'):
    scheduler = BackgroundScheduler(daemon=False)

    scheduler.add_job(lambda: expired_queue_item_cleaner(app, db),
                      'cron',
                      id="queue_cleaner",
                      name="queue_cleaner",
                      hour='8',
                      minute='0',
                      replace_existing=True)

    scheduler.add_job(lambda: expired_reservations_cleaner(app, db),
                      'interval',
                      id="reservations_cleaner",
                      name="reservations_cleaner",
                      minutes=15)

    return scheduler


def configure_application(no_scheduler=False):
    app = create_app()

    @event.listens_for(Engine, "connect")
    def connect(dbapi_connection, _):
        dbapi_connection.create_function("get_shift_date", 3, get_shift_date)

    if not no_scheduler:
        scheduler = configure_scheduler(app, db)

        scheduler.start()

    return app


if __name__ == '__main__':
    app = configure_application(no_scheduler=True)

    app.run(port=get_application_port())
