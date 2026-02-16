import os


class Config:
    # This key keeps your web sessions secure
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'thesis-development-key-2024'

    # --- Azure SQL Configuration ---
    DB_SERVER = "homeplate-sql-srv.database.windows.net"
    DB_NAME = "homeplate-db"
    DB_USER = "dbadmin"
    DB_PASS = "Password1"

    # This tells SQLAlchemy to use the ODBC Driver (pre-installed on Azure B1)
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_SERVER}/{DB_NAME}?"
        "driver=ODBC+Driver+17+for+SQL+Server"
    )

    # Disabling tracking saves memory and prevents overhead on your B1 tier
    SQLALCHEMY_TRACK_MODIFICATIONS = False