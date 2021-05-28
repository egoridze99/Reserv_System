from flask import Flask, render_template
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

jwt = JWTManager(app)

db = SQLAlchemy(app)