# Reaches into the app folder
# Because an __init__.py exist on the top level of the app folder, the whole folder is treated as a package
# looks for the create_app()
from app import create_app

# This is the off/on switch for the application, the entry point
# Application Factory Pattern
# "Build it now"
# app is a Flask object
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)