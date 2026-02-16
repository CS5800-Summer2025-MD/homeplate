import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'thesis-development-key-2024'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Check if we are running a test
    if os.environ.get('FLASK_ENV') == 'testing':
        # Use a simple, local SQLite database for GitHub tests
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    else:
        # Your actual Azure SQL credentials
        DB_SERVER = "homeplate-sql-srv.database.windows.net"
        DB_NAME = "homeplate-db"
        DB_USER = "dbadmin"
        DB_PASS = "Password1"  # Replace with your real password

        SQLALCHEMY_DATABASE_URI = (
            f"mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_SERVER}/{DB_NAME}?"
            "driver=ODBC+Driver+17+for+SQL+Server"
        )