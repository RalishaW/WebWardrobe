import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'please-change-me')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_PROFILE_PICTURE = 'app/static/profile_picture'
    UPLOAD_CLOTHING_ITEM = 'app/static/clothing_items'
    MAKE_OUTFIT = 'app/static/outfits'

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    @staticmethod
    def init_app(app):
        # ensure instance folder exists
        os.makedirs(app.instance_path, exist_ok=True)
        # default SQLite database in instance folder
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            'sqlite:///' + os.path.join(app.instance_path, 'fashanise.db')
        )
        # ensure upload folders exist
        for folder in (
            app.config['UPLOAD_PROFILE_PICTURE'],
            app.config['UPLOAD_CLOTHING_ITEM'],
            app.config['MAKE_OUTFIT'],
        ):
            os.makedirs(folder, exist_ok=True)

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    # in-memory DB for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
