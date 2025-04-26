from app import db



# ----------------------
# User Model
# ----------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Will store hashed password later

    wardrobe_items = db.relationship('ClothingItem', backref='user', lazy=True)
    outfits = db.relationship('Outfit', backref='user', lazy=True)

# ----------------------
# Clothing Item Model
# ----------------------
class ClothingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)  # File path to uploaded image
    color = db.Column(db.String(50))
    season = db.Column(db.String(50))
    clothing_type = db.Column(db.String(50))
    occasion = db.Column(db.String(50))
    body_part = db.Column(db.String(50))                 # 4 parts: head, body, legs, foot


    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ----------------------
# Outfit Model
# ----------------------
class Outfit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    privacy = db.Column(db.String(20), nullable=False)  # 'public' or 'private'
    preview_image = db.Column(db.String(200))  # file path to generated outfit preview

    occasion = db.Column(db.String(50))
    season = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
