import os


class Config:
    DEBUG = os.environ.get('DEBUG') or True
    SQLALCHEMY_DATABASE_URI = r'sqlite:///./db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'Sy6e_r!^qwer.dedez'
    FLASK_ADMIN_SWATCH = 'cerulean'
    SECRET_KEY = 'Sy6e_r!^qwer.dedez'
