import os 
import sys 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail

from .config import Config, config_dict

# Extension instances
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)

    #Use TestingConfig if running via unittest
    if 'unittest' in sys.modules:
        config_object = config_dict['testing']
    else:
        config_object = config_dict['default']

    app.config.from_object(config_object)

    app.config['CONFIG_CLASS'] = config_object

    if hasattr(config_object, 'init_app'):
        config_object.init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    mail.init_app(app)

    # User loader for Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprint
    from app.blueprints import main as main_bp
    app.register_blueprint(main_bp)

    return app
