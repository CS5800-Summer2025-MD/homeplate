import os


class Config:
    # Flask uses this for session security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'

    # Points to Azure SQL Database for persistent storage
    # We use a local fallback so the site stays 'up' during development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///homeplate.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False