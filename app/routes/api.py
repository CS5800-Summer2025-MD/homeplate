from flask import Blueprint, jsonify
from app.models import Recipe

# This defines the "api" section of your website
api_bp = Blueprint('api', __name__)

@api_bp.route('/api/recipes', methods=['GET'])
def get_recipes():
    # For now, we return an empty list until the DB is connected
    return jsonify([])