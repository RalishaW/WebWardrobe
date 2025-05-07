from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import os

# Initialize extensions 
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

# Configs
class Config:
    SECRET_KEY = 'SECRET_KEY'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_PROFILE_PICTURE = 'app/static/images/profile_picture'
    UPLOAD_CLOTHING_ITEM = 'app/static/images/clothing_items'
    MAKE_OUTFIT = 'app/static/images/outfits'

    # Mail server
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'fashanize@gmail.com'
    MAIL_PASSWORD = 'gikg xlif fdce qsmq'
    
    @staticmethod
    def init_app(app):
        os.makedirs(app.instance_path, exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'fashanise.db')
        for folder in [
            Config.UPLOAD_PROFILE_PICTURE,
            Config.UPLOAD_CLOTHING_ITEM,
            Config.MAKE_OUTFIT
        ]: 
            os.makedirs(folder, exist_ok=True)

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)


# Initialize binded app extensions 
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
login_manager.init_app(app)
login_manager.login_view = 'login'


# Import models 
from app.models import User

# Load users for flask_login
@login_manager.user_loader
def load_user(user_id):  
    user = User.query.get(int(user_id))
    if user is None:
        abort(404)
    return user
    
# Import routes
from app import routes

