from flask import Blueprint, render_template, request, redirect, url_for, send_file
from app import db
from app.models import Recipe, Interaction, User
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)

    # 1. Main Pagination (Still needs order_by for Azure)
    pagination = Recipe.query.order_by(Recipe.id.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    recipes = pagination.items

    # 2. Dynamic Randomization Logic
    # Check if we are using SQLite (testing) or MSSQL (Azure)
    engine_name = db.engine.name
    if engine_name == 'sqlite':
        random_func = func.random()
    else:
        random_func = func.newid()  # For Azure SQL / MSSQL

    suggested = Recipe.query.order_by(random_func).limit(1).all()

    return render_template('index.html', recipes=recipes, pagination=pagination, suggested=suggested)

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


@main_bp.route('/download_pdf')
def download_pdf():
    # 1. Get IDs from the URL (from your JavaScript)
    ids_string = request.args.get('ids', '')
    if not ids_string:
        return "No recipes selected", 400

    recipe_ids = ids_string.split(',')
    recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()

    # 2. Setup the "In-Memory" PDF file
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    # 3. Define Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    body_style = styles['BodyText']

    # Create a custom style for the 'Cuisine' tag
    cuisine_style = ParagraphStyle('CuisineStyle', parent=styles['Italic'], fontSize=10, textColor='#6f5f5c')

    # 4. Build the Content
    elements = []

    # Main Header
    elements.append(Paragraph("Your Recipe Collection", title_style))
    elements.append(Spacer(1, 0.25 * inch))

    for recipe in recipes:
        # Recipe Title
        elements.append(Paragraph(recipe.title, heading_style))
        # Cuisine
        elements.append(Paragraph(f"Cuisine: {recipe.cuisine}", cuisine_style))
        elements.append(Spacer(1, 0.1 * inch))

        # Ingredients Section
        elements.append(Paragraph("<b>Ingredients:</b>", body_style))
        # We replace newlines with <br/> for the PDF
        ingredients_formatted = recipe.ingredients.replace('\n', '<br/>')
        elements.append(Paragraph(ingredients_formatted, body_style))
        elements.append(Spacer(1, 0.1 * inch))

        # Instructions Section
        elements.append(Paragraph("<b>Instructions:</b>", body_style))
        instructions_formatted = recipe.instructions.replace('\n', '<br/>')
        elements.append(Paragraph(instructions_formatted, body_style))

        # Add a line or space between recipes
        elements.append(Spacer(1, 0.4 * inch))
        elements.append(Paragraph("<hr/>", body_style))  # Simple horizontal line

    # 5. Generate PDF
    doc.build(elements)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name="my_recipes.pdf",
                     mimetype='application/pdf')