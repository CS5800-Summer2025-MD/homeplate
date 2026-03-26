from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Recipe, Interaction, User
from app.recommendation import get_recommendations
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    recipes = Recipe.query.all()
    suggested = get_recommendations()
    return render_template('index.html', recipes=recipes, suggested=suggested)

@main_bp.route('/add', methods=['GET', 'POST'])
@login_required
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


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 1. Scramble the password so even you can't read it in Azure
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')

        # 2. Create the "User" object using your Model
        new_user = User(username=username, password_hash=hashed_pw)

        # 3. Save it to Azure SQL
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 1. Find the user in Azure by their username
        user = User.query.filter_by(username=request.form.get('username')).first()

        # 2. Check if the password they typed matches the hashed one in the DB
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            # 3. THIS IS THE CRITICAL LINE
            login_user(user)
            return redirect(url_for('main.index'))

    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))