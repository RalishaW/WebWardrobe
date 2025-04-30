from app import db

# ----------------------
# User Model
# ----------------------
class User(db.Model):
    __tablename__ = 'users'

    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(128), nullable=False)  # Will store hashed password later
    profile_picture = db.Column(db.String, default='images/empty-profile-pic.png')

    wardrobe_items = db.relationship('ClothingItem', backref='user', lazy=True)
    outfits = db.relationship('Outfit', backref='user', lazy=True)

# ----------------------
# Clothing Item Model
# ----------------------
class ClothingItem(db.Model):
    __tablename__ = 'clothing_items'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False, nullable=True)  # File path to uploaded image
    color = db.Column(db.String(50),)
    season = db.Column(db.String(50))
    clothing_type = db.Column(db.String(50))
    occasion = db.Column(db.String(50))
    email = db.Column(db.String, db.ForeignKey('users.email'), nullable=False)

# ----------------------
# Outfit Model
# ----------------------
class Outfit(db.Model):
    __tablename__ = 'outfits'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    privacy = db.Column(db.String(20), nullable=False)  # 'public' or 'private'
    preview_image = db.Column(db.String(200))  # file path to generated outfit preview
    occasion = db.Column(db.String(50))
    season = db.Column(db.String(50))
    email = db.Column(db.String, db.ForeignKey('users.email'), nullable=False)


