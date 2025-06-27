import unittest
from app import app, recipes

### to run use the cmd 'python -m unittest discover tests" from terminal

class RecipeAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        recipes.clear()

    def test_homepage_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Recipes', response.data)

    def test_add_recipe_success(self):
        response = self.app.post('/add', data={
            'title': 'Test Pancakes',
            'ingredients': 'Flour, Eggs, Milk',
            'instructions': 'Mix and cook'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Pancakes', response.data)

    def test_delete_nonexistent_recipe(self):
        response = self.app.post('/delete/9999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Recipe not found', response.data)

if __name__ == '__main__':
    unittest.main()
