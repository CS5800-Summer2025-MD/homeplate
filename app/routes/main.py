from flask import Blueprint, render_template
from app.models import Recipe

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch all recipes from your new Azure SQL Database
    recipes = Recipe.query.all()
    # Pass them to the HTML template
    return render_template('index.html', recipes=recipes)