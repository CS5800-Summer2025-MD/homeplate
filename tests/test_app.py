import unittest
import os

# THIS MUST COME FIRST: Tell the config file to use SQLite, not Azure SQL
os.environ['FLASK_ENV'] = 'testing'

from app import create_app, db

class RecipeAppTestCase(unittest.TestCase):
    def setUp(self):
        # Initialize the app - it will now see FLASK_ENV and pick SQLite
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'HomePlate++', response.data)