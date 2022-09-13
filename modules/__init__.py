from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '4YrzfpQ4kGXjuP6w'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'

from modules import routes
