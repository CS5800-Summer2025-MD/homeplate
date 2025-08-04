import json
import os
import io
from flask import Flask, render_template, request, redirect, url_for, send_file
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

DATA_FILE = 'recipes.json'
RECIPES_PER_PAGE = 6

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
@app.route('/page/<int:page>')
def index(page=1):
    start = (page - 1) * RECIPES_PER_PAGE
    end = start + RECIPES_PER_PAGE
    total_pages = (len(recipes) + RECIPES_PER_PAGE - 1) // RECIPES_PER_PAGE
    paginated = recipes[start:end]
    return render_template('index.html', recipes=paginated, page=page, total_pages=total_pages)

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    if 0 <= recipe_id < len(recipes):
        return render_template('recipe.html', recipe=recipes[recipe_id], recipe_id=recipe_id)
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

@app.route('/delete/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    if 0 <= recipe_id < len(recipes):
        del recipes[recipe_id]
        save_recipes()
    return redirect(url_for('index'))


@app.route('/download_multiple', methods=['POST'])
def download_multiple():
    selected_ids_str = request.form.get('selected_ids', '')
    if not selected_ids_str:
        return "No recipes selected", 400

    try:
        selected_ids = list(map(int, selected_ids_str.split(',')))
    except ValueError:
        return "Invalid recipe IDs", 400

    selected = [recipes[i] for i in selected_ids if 0 <= i < len(recipes)]
    if not selected:
        return "No valid recipes found", 400

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    y = 800
    for recipe in selected:
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y, recipe['title'])
        y -= 20
        p.setFont("Helvetica", 12)
        p.drawString(100, y, "Ingredients:")
        y -= 15
        for line in recipe['ingredients'].split('\n'):
            p.drawString(120, y, line)
            y -= 15
        p.drawString(100, y, "Instructions:")
        y -= 15
        for line in recipe['instructions'].split('\n'):
            p.drawString(120, y, line)
            y -= 15
        y -= 30
        if y < 100:
            p.showPage()
            y = 800
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="recipes.pdf", mimetype='application/pdf')



if __name__ == '__main__':
    app.run(debug=True)

