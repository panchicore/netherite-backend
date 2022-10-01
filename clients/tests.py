from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import Company, Account


class SimpleTest(TestCase):
    fixtures = [
        "accounts/fixtures/tests/groups.json",
        "accounts/fixtures/tests/users.json",
        "accounts/fixtures/tests/companies.json",
        "accounts/fixtures/tests/accounts.json",
        "clients/fixtures/tests/clients.json",
    ]

    def get_account(self):
        return self.client.get('/api/1/accounts/').json()[0]

    def get_account_header(self):
        account_uuid = self.get_account().get("uuid")
        return {'HTTP_X_ACCOUNT': account_uuid}

    def test_clients_get(self):
        # only clients owned by the user's company current account
        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        response = self.client.get('/api/1/clients/', **self.get_account_header())
        self.assertEqual(response.status_code, 200)
        clients = response.json()
        current_account_company_id = self.get_account().get("company")
        for c in clients:
            self.assertEqual(c.get("company"), current_account_company_id)

    def test_client_post(self):
        company = Company.objects.get(name="C1 Logistics")
        data = {
            "name": "New client for C1",
            "company": company.id
        }

        # not logged in
        response = self.client.post('/api/1/clients/', data=data)
        self.assertEqual(response.status_code, 403)

        # logged in without permissions - (a driver)
        user = User.objects.get(username="c1driver")
        self.client.force_login(user)
        response = self.client.post('/api/1/clients/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 403)

        # logged in with permissions but not part of user account companies
        user = User.objects.get(username="c2logistics")
        self.client.force_login(user)
        response = self.client.post('/api/1/clients/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 400)
        errors = response.json()
        self.assertTrue('company' in errors)

        # logged in with permissions and with its user account companies
        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        response = self.client.post('/api/1/clients/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 201)

        # client created by the user
        new_client = response.json()
        self.assertEqual(user.id, new_client['created_by'])

        # avoid duplication of clients
        response = self.client.post('/api/1/clients/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 400)



