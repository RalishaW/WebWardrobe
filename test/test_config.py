import os
import app

class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'SECRET_KEY'
    UPLOAD_CLOTHING_ITEM = 'test/static/clothing_items'
    MAKE_OUTFIT          = 'test/static/outfits'
    UPLOAD_PROFILE_PICTURE = 'test/static/profile_picture'