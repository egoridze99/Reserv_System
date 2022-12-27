from app import app
from admin import admin
from Schedule.blueprint import schedule_blueprint
from Admin.blueprint import admin_blueprint
from Certificate.blueprint import certificate_blueprint

app.register_blueprint(schedule_blueprint, url_prefix='/api')
app.register_blueprint(admin_blueprint, url_prefix='/admin/')
app.register_blueprint(certificate_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run()
