from app import app
from admin import admin
from Schedule.blueprint import schedule
from Admin.blueprint import admin

app.register_blueprint(schedule, url_prefix='/api/')
app.register_blueprint(admin, url_prefix='/admin_api/')


if __name__ == '__main__':
    app.run()
