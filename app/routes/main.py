# tools to handle URLs, send users to new pages, and read data in
from flask import Blueprint, render_template, request, redirect, url_for, send_file, current_app
# do calcs on db data
from app import db
from app.models import Recipe, Interaction, User
from sqlalchemy import func
# hide password
from werkzeug.security import generate_password_hash, check_password_hash
# protect certain pages with @login_required
from flask_login import login_user, logout_user, login_required
# create the pdf
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO

from groq import Groq
from dotenv import load_dotenv
# convert AI response to html
import markdown
import os
from sqlalchemy import or_

load_dotenv()
# connect to the llama 3 model
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
# the plug is named main
main_bp = Blueprint('main', __name__)

# connects the function index() to /
# when someone lands on this page, execute this method
@main_bp.route('/')
def index():
    # 1. Get the current page from the URL (default to 1)
    page = request.args.get('page', 1, type=int)

    # 2. Standard Pagination: Show 6 recipes per page, newest first
    pagination = Recipe.query.order_by(Recipe.id.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    recipes = pagination.items

    # 3. Environment Check: Choose the correct Random function -- due to local testing, git tests, and prod env
    database_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')

    if 'sqlite' in database_uri:
        rand_func = func.random()  # Works for local SQLite tests
    else:
        rand_func = func.newid()  # Works for Azure SQL (Production)

    # 4. Smart Logic: Find the most frequent Cuisine in the Database
    top_cuisine_query = db.session.query(
        Recipe.cuisine,
        func.count(Recipe.cuisine).label('qty')
    ).group_by(Recipe.cuisine).order_by(func.count(Recipe.cuisine).desc()).first()

    # 5. Get a Recommendation based on that top cuisine
    if top_cuisine_query:
        fav_cuisine = top_cuisine_query[0]
        # Get one random recipe from the favorite cuisine category
        suggested = Recipe.query.filter_by(cuisine=fav_cuisine).order_by(rand_func).limit(1).all()
    else:
        # Fallback if the database is empty or has no cuisines
        suggested = []

    # 6. Render the page with all the data
    return render_template(
        'index.html',
        recipes=recipes,
        pagination=pagination,
        suggested=suggested
    )

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
        db.session.add(new_recipe) # like git add, git commit
        db.session.commit() # This saves it to Azure!
        return redirect(url_for('main.index'))
    return render_template('add_recipe.html')

@main_bp.route('/delete/<int:id>')
@login_required
def delete_recipe(id):
    recipe_to_delete = Recipe.query.get_or_404(id)
    db.session.delete(recipe_to_delete)
    db.session.commit() # This removes it from Azure!
    return redirect(url_for('main.index'))

# id gets sent to the function
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
            # 3. THIS IS THE CRITICAL LINE from flask-login
            login_user(user)
            return redirect(url_for('main.index'))

    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    # from flask-login
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


@main_bp.route('/ai-planner')
def ai_planner():
    return render_template('ai_planner.html')

@main_bp.route('/generate-ai-plan', methods=['POST'])
@login_required
def generate_ai_plan():
    user_request = request.form.get('user_prompt')

    all_recipes = Recipe.query.all()

    recipe_context = []
    for r in all_recipes:
        recipe_context.append(f"ID: {r.id} | Title: {r.title} | Cuisine: {r.cuisine} | Ingredients: {r.ingredients}")

    context_str = "\n".join(recipe_context)

    system_prompt = f"""
    You are a professional meal planner. Use the following user collection to satisfy this request: "{user_request}"

    Available Recipes:
    {context_str}


    STRICT FORMATTING RULES:
        1. Organize the plan by Day (e.g., Day 1, Day 2).
        2. DO NOT include Database IDs.
        3. DO NOT use the phrase "(Manual Addition)".
        4. For every recipe, use this exact structure with DOUBLE SPACING:
           **[Meal Type]: [Recipe Name]**
           Ingredients: [List ingredients]
           Quick Directions:
           [Summarized directions on this new line]
        
        5. Only use ONE empty line between different meals
        6. IMPORTANT: You MUST put exactly one empty line between the Ingredients and the Quick Directions header.
        7. After all meals for a specific Day are finished, add a horizontal line (---).
        
    """

    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": system_prompt}]
    )

    raw_markdown = completion.choices[0].message.content
    html_plan = markdown.markdown(raw_markdown)

    return render_template('meal_plan_view.html', plan=html_plan)



@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        # Search for the query string in title, ingredients, or cuisine
        results = Recipe.query.filter(
            or_(
                Recipe.title.ilike(f'%{query}%'),
                Recipe.ingredients.ilike(f'%{query}%'),
                Recipe.cuisine.ilike(f'%{query}%')
            )
        ).all()
    else:
        results = []

    return render_template('index.html', recipes=results, search_query=query)

