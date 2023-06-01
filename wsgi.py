from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from config import Config

from domains import references_blueprint, reservations_blueprint, money_blueprint, certificate_blueprint, \
    queue_blueprint, base_blueprint, admin_blueprint

from db import db
from services import Scheduler
from models import *


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

    # CONFIGURING ADMIN PANEL
    admin_panel = Admin(flask_app, name='film_is_scheduler', template_mode='bootstrap3', url="/flask_admin_panel")
    admin_panel.add_view(ModelView(Cinema, db.session))
    admin_panel.add_view(ModelView(Room, db.session))
    admin_panel.add_view(ModelView(Guest, db.session))
    admin_panel.add_view(ModelView(Reservation, db.session))
    admin_panel.add_view(ModelView(User, db.session))
    admin_panel.add_view(ModelView(Checkout, db.session))
    admin_panel.add_view(ModelView(Money, db.session))
    admin_panel.add_view(ModelView(UpdateLogs, db.session))
    admin_panel.add_view(ModelView(Certificate, db.session))

    # CONFIGURING SCHEDULER
    background_scheduler = BackgroundScheduler()
    scheduler = Scheduler(background_scheduler, db, flask_app)
    scheduler.register_clear_expired_queue_items_timer()

    return flask_app, scheduler


if __name__ == '__main__':
    app, scheduler = create_app()

    scheduler.start()
    app.run()

