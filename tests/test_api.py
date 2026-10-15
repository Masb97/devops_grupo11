import unittest
from app import create_app
from app.extensions import db


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True,
                               "SQLALCHEMY_DATABASE_URI": "sqlite://",
                               "JWT_SECRET_KEY": "test-secret-" * 4})
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_auth_flow(self):
        data = {"email": "user@example.com", "password": "password123"}
        response = self.client.post("/api/auth/register", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password_hash", response.json)
        self.assertEqual(self.client.post("/api/auth/register", json=data).status_code, 409)
        token = self.client.post("/api/auth/login", json=data).json["access_token"]
        response = self.client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["email"], data["email"])
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        data["password"] = "incorrect-password"
        self.assertEqual(self.client.post("/api/auth/login", json=data).status_code, 401)

    def test_validation_and_health(self):
        for data in ({}, {"email": "invalid", "password": "short"}, []):
            self.assertEqual(self.client.post("/api/auth/register", json=data).status_code, 400)
        self.assertEqual(self.client.get("/health").status_code, 200)
