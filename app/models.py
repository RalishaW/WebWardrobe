from app import db
from flask_login import UserMixin
from sqlalchemy.orm import validates
from sqlalchemy import Enum
from datetime import datetime, timezone

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
    dob = db.Column(db.Date, nullable=True)
    height = db.Column(db.Integer, nullable=True)

    wardrobe_items = db.relationship('ClothingItem', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    outfits = db.relationship('Outfit', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_shared = db.relationship('SharedOutfit', foreign_keys='SharedOutfit.sender_id', cascade='all, delete-orphan', backref='sender_user')
    received_shared = db.relationship('SharedOutfit', foreign_keys='SharedOutfit.receiver_id', cascade='all, delete-orphan', backref='receiver_user')

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
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    outfit_name = db.Column(db.String(100), nullable=False)
    preview_image = db.Column(db.String(200))           # file path to generated outfit preview
    occasion = db.Column(db.String(50))
    season = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# ----------------------
# Outfit Item Model (Link between Outfit and ClothingItem)
# ----------------------

class OutfitItem(db.Model):
    __tablename__ = 'outfit_items'

    id = db.Column(db.Integer, primary_key=True)
    outfit_id = db.Column(db.Integer, db.ForeignKey('outfits.id'), nullable=False)
    clothing_item_id = db.Column(db.Integer, db.ForeignKey('clothing_items.id'), nullable=False)

    # Optional: Relationship backrefs (if needed later)
    outfit = db.relationship("Outfit", backref=db.backref("outfit_items", cascade="all, delete-orphan"))
    clothing_item = db.relationship("ClothingItem")

class SharedOutfit(db.Model):
    __tablename__ = 'shared_outfit'
    id = db.Column(db.Integer, primary_key=True)
    outfit_id = db.Column(db.Integer, db.ForeignKey('outfits.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    outfit = db.relationship('Outfit', backref=db.backref('shared_entries', cascade='all, delete-orphan'))
    sender = db.relationship('User', foreign_keys=[sender_id], overlaps="sender_user,sent_shared")
    receiver = db.relationship('User', foreign_keys=[receiver_id], overlaps="receiver_user,received_shared")
