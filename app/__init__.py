from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# Initialize Flask App
app = Flask(__name__)

# Configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'fashanise.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key_here"
os.makedirs(app.instance_path, exist_ok=True)
app.config['UPLOAD_PROFILE_PICTURE'] = 'app/static/images/profile_picture'
app.config['UPLOAD_CLOTHING_ITEM'] = 'app/static/images/clothing_items'
app.config['MAKE_OUTFIT'] = 'app/static/images/outfits'

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload folder exists
upload_folder = app.config['UPLOAD_PROFILE_PICTURE']
os.makedirs(upload_folder, exist_ok=True)

from app.models import User
from app import routes

@login_manager.user_loader
def load_user(user_id):  
    return User.query.get(int(user_id))

