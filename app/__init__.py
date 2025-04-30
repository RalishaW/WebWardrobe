from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

# Intialize Flask App
app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'fashanise.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key_here"
os.makedirs(app.instance_path, exist_ok=True)
app.config['UPLOAD_PROFILE_PICTURE'] = 'app/static/images/profile_picture'
app.config['UPLOAD_CLOTHING_ITEM'] = 'app/static/images/clothing_items'
app.config['MAKE_OUTFIT'] = 'app/static/images/outfits'

db.init_app(app)

# Ensure upload folder exists
upload_folder = app.config['UPLOAD_PROFILE_PICTURE']
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)


from app import routes, models