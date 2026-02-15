import unittest
from app import create_app, db


class RecipeAppTestCase(unittest.TestCase):
    def setUp(self):
        # 1. Initialize the app using the factory
        self.app = create_app()
        self.app.config['TESTING'] = True

        # 2. Use a local memory-only database for testing (fast and clean)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        # 3. Create a test client
        self.client = self.app.test_client()

        # 4. Set up the database tables within the app context
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up the database after every test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_homepage_loads(self):
        # Testing the new modular route
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Note: Adjust this string if your main.py route returns different text
        self.assertIn(b'HomePlate++', response.data)

    # We will re-enable test_add_recipe once we finish the Week 2 Models