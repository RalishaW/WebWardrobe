from app import db
from flask_login import UserMixin
from sqlalchemy.orm import validates
from sqlalchemy import Enum

# ----------------------
# User Model
# ----------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    def get_id(self):
        return self.id
    
    @validates('email')
    def validate_email(self, key, email):
        assert '@' in email, 'Invalid email'
        return email

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Will store hashed password later
    profile_picture = db.Column(db.String, default='images/empty-profile-pic.png')

    wardrobe_items = db.relationship('ClothingItem', backref='user', lazy='dynamic')
    outfits = db.relationship('Outfit', backref='user', lazy='dynamic')

# ----------------------
# Clothing Item Model
# ----------------------
class ClothingItem(db.Model):
    __tablename__ = 'clothing_items'

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)  # File path to uploaded image
    color = db.Column(db.String(50))
    season = db.Column(db.String(50))
    type = db.Column(db.String(50))
    occasion = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# ----------------------
# Outfit Model
# ----------------------
class Outfit(db.Model):
    __tablename__ = 'outfits'

    id = db.Column(db.Integer, primary_key=True)
    outfit_name = db.Column(db.String(100), nullable=False)
    privacy = db.Column(Enum('public', 'private', name='privacy-enum'), nullable=False)  # 'public' or 'private'
    preview_image = db.Column(db.String(200))           # file path to generated outfit preview
    occasion = db.Column(db.String(50))
    season = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
