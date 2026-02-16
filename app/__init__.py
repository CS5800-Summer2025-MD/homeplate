from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Create the db object globally, but initialize it inside the factory
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize the database with the app
    db.init_app(app)

    # Register Blueprints (Main and API)
    from .routes.main import main_bp
    from .routes.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Import models here so the database knows the tables exist
    with app.app_context():
        from . import models
        # This line will actually create the tables in Azure if they don't exist
        db.create_all()

    return app