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