from django.contrib.auth.models import User
from django.test import TestCase


class SimpleTest(TestCase):
    fixtures = [
        "accounts/fixtures/tests/groups.json",
        "accounts/fixtures/tests/users.json",
        "accounts/fixtures/tests/companies.json",
        "accounts/fixtures/tests/accounts.json",
    ]

    def test_login(self):
        response = self.client.post('/api/auth/login/', data={"username": "c1logistics", "password": "C1?holamundo"})
        self.assertEqual(response.status_code, 200)

    def test_account_http_header(self):
        # only accounts for logged in users
        accounts = self.client.get('/api/1/accounts/')
        self.assertEqual(accounts.status_code, 403)

        # logged in users accounts
        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        accounts = self.client.get('/api/1/accounts/')
        self.assertEqual(accounts.status_code, 200)
        uuid = accounts.json()[0].get("uuid")
        self.assertEqual(uuid, "6e506783-c71a-4f58-8b70-30c00e045d73")
