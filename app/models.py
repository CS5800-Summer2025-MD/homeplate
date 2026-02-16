from . import db
from datetime import datetime

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    cuisine = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Interaction(db.Model):
    __tablename__ = 'interactions'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    interaction_type = db.Column(db.String(50)) # e.g., 'view', 'click'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)