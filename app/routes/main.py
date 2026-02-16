from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Recipe

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch all recipes from your new Azure SQL Database
    recipes = Recipe.query.all()
    # Pass them to the HTML template
    return render_template('index.html', recipes=recipes)

@main_bp.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        # Get data from the form
        new_recipe = Recipe(
            title=request.form.get('title'),
            cuisine=request.form.get('cuisine'),
            ingredients=request.form.get('ingredients'),
            instructions=request.form.get('instructions')
        )
        db.session.add(new_recipe)
        db.session.commit() # This saves it to Azure!
        return redirect(url_for('main.index'))
    return render_template('add_recipe.html')

@main_bp.route('/delete/<int:id>')
def delete_recipe(id):
    recipe_to_delete = Recipe.query.get_or_404(id)
    db.session.delete(recipe_to_delete)
    db.session.commit() # This removes it from Azure!
    return redirect(url_for('main.index'))