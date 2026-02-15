from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize the database object
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize the database with the app settings
    db.init_app(app)

    # Register Blueprints (Modules)
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app