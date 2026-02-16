from flask import Blueprint, jsonify
from app.models import Recipe

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/recipes', methods=['GET'])
def get_recipes():
    # Fetch all recipes from Azure SQL
    recipes = Recipe.query.all()

    # Convert SQL objects into a list of dictionaries (JSON)
    recipe_list = []
    for r in recipes:
        recipe_list.append({
            'id': r.id,
            'title': r.title,
            'cuisine': r.cuisine,
            'ingredients': r.ingredients,
            'instructions': r.instructions
        })

    return jsonify(recipe_list)