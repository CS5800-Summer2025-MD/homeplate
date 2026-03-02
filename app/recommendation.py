from app.models import Recipe, Interaction
from sqlalchemy import func


def get_recommendations():
    # 1. Find the most viewed cuisine for this user
    top_cuisine = Recipe.query.join(Interaction).with_entities(
        Recipe.cuisine, func.count(Interaction.id).label('view_count')
    ).group_by(Recipe.cuisine).order_by(func.count(Interaction.id).desc()).first()

    if not top_cuisine:
        return []
    # 2. Find other recipes with that same cuisine
    recommendations = Recipe.query.filter_by(cuisine=top_cuisine.cuisine).limit(3).all()

    return recommendations