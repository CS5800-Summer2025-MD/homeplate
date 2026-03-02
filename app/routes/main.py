from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Recipe, Interaction
from app.recommendation import get_recommendations

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    recipes = Recipe.query.all()
    suggested = get_recommendations()
    return render_template('index.html', recipes=recipes, suggested=suggested)

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

@main_bp.route('/recipe/<int:id>')
def recipe_detail(id):
    recipe = Recipe.query.get_or_404(id)

    # Log the interaction!
    new_interaction = Interaction(recipe_id=id, interaction_type='view')
    db.session.add(new_interaction)
    db.session.commit()

    return render_template('recipe_detail.html', recipe=recipe)
