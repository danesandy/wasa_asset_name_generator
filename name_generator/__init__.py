from flask import Flask, session
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager, UserMixin
from dotenv import load_dotenv
from flask_session import Session

load_dotenv()
app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
CORS(app)
# Session(app)
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:superstar9@localhost/asset_code_names'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# from name_generator import views
from .models import *
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))