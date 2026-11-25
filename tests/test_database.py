"""Simple SQLite schema tests; Flask is required to run them."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from app import create_app
from database import get_db


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        path = str(Path(self.temp.name) / "shopping.sqlite3")
        self.app = create_app({"TESTING": True, "DATABASE": path, "SECRET_KEY": "test-only"})

    def tearDown(self):
        self.temp.cleanup()

    def test_user_and_list_tables_exist(self):
        with self.app.app_context():
            db = get_db()
            names = {row["name"] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertTrue({"users", "shopping_lists", "list_items"}.issubset(names))

    def test_registration_and_list(self):
        client = self.app.test_client()
        response = client.post("/register", data={"username": "student", "password": "password123"})
        self.assertEqual(response.status_code, 302)
        response = client.post("/login", data={"username": "student", "password": "password123"})
        self.assertEqual(response.status_code, 302)
        response = client.post("/lists", data={"name": "Groceries", "store": "Market"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"Groceries", client.get("/lists").data)
        response = client.post("/lists/1/items", data={"name": "Milk", "quantity": "2", "price": "5.25"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"10.50", client.get("/lists/1").data)


if __name__ == "__main__":
    unittest.main()
