import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = 'recipes.json'

def load_recipes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_recipes():
    with open(DATA_FILE, 'w') as f:
        json.dump(recipes, f, indent=2)

recipes = load_recipes()

@app.route('/')
def index():
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    if 0 <= recipe_id < len(recipes):
        return render_template('recipe.html', recipe=recipes[recipe_id])
    return "Recipe not found", 404

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        recipes.append({
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions
        })
        save_recipes()
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

if __name__ == '__main__':
    app.run(debug=True)
