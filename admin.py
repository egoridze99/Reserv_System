from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app, db
from models import *


admin = Admin(app, name='seans', template_mode='bootstrap3')
admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Guest, db.session))
admin.add_view(ModelView(Reservation, db.session))
admin.add_view(ModelView(AdminUser, db.session))
admin.add_view(ModelView(Checkout, db.session))
admin.add_view(ModelView(Money, db.session))
