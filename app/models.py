from __init__ import db

# Database structure
# Create class for each object: user, clothing (wardrobe), outfit (object)
# User database, clothes database

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    
    # one-to-many relationship: one user owns many items
    items = db.relationship('Item', backref='owner', lazy=True)
    outfits = db.relationship('Outfit', backref='creator', lazy=True)


class Item(db.Model):
    image_address = db.Column(db.Text, nullable=False)          # storing address of the image in database file
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body_part = db.Column(db.String(50), nullable=False)        # e.g., head, body, legs, feet
    category = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(20))
    condition = db.Column(db.String(50))                    
    origin = db.Column(db.String(100))                           # e.g., thrifted, vintage, etc.
    purchase_price = db.Column(db.Float)
    date_purchased = db.Column(db.Date)
    main_color = db.Column(db.String(50))
    additional_colors = db.Column(db.String(100))
    pattern = db.Column(db.String(100))
    material = db.Column(db.String(100))
    secondary_material = db.Column(db.String(100))
    style = db.Column(db.String(100))
    neckline = db.Column(db.String(50))
    sleeve_length = db.Column(db.String(50))
    season = db.Column(db.String(50))  # e.g., summer, winter
    occasion = db.Column(db.String(50))  # e.g., casual, beach, gym
    personal_notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# combination of category: head, body {accesories, shirt, jackets, scarves, gloves}, legs and feet {shoes}
class Outfit(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    season = db.Column(db.String(50))
    occasion = db.Column(db.String(50))
    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Composition: 4 parts - head, body, legs, feet
    head_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)       # head could be optional
    body_item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    legs_item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    feet_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)       # feet could be optional


# User -> own many -> Items
# User -> own many -> Outfits
# Outift -> Uses 4 items (2 optional: head and feet): body, legs
# Problem:
"""
    Problem:
    - How do we have one outfit with multiple body items such as scarves, necklace, t-shirt, jacket etc in the display.
    - To make the implementation more simple, reduce to only one item per body part. Any suggestions?
"""
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

    outfit = db.relationship('Outfit', backref='shared_entries')
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
