import os.path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import Company
from drivers.models import Driver, DriverDocument


class SimpleTest(TestCase):
    fixtures = [
        "accounts/fixtures/tests/groups.json",
        "accounts/fixtures/tests/users.json",
        "accounts/fixtures/tests/companies.json",
        "accounts/fixtures/tests/accounts.json",
        "drivers/fixtures/tests/drivers.json",
        "drivers/fixtures/tests/drivers_docs.json",
    ]

    def get_account(self):
        response = self.client.get('/api/1/accounts/')
        self.assertEqual(response.status_code, 200, response.json())
        return response.json()[0]

    def get_account_header(self):
        account_uuid = self.get_account().get("uuid")
        return {'HTTP_X_ACCOUNT': account_uuid}

    def _get_driver_payload_for_post(self):
        company = Company.objects.get(name="C1 Logistics")
        data = {
            "first_name": "Driver 2",
            "last_name": "C1",
            "identification_type": "national-id",
            "identification": "1234",
            "company": company.id
        }
        return company, data

    def _get_driver_document_payload_for_post(self, driver):
        company1 = Company.objects.get(name="C1 Logistics")
        file = open(os.path.join(settings.BASE_DIR, 'README.md'), 'r', encoding='utf-8')
        data = {
            "company": company1.id,
            "driver": driver.id,
            "type": "identification",
            "file": file
        }
        return data

    def test_drivers_get_by_coordinator(self):
        """
        Valid: when the coordinator has account for the company
        Expect: a list of all companies drivers
        """
        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        response = self.client.get('/api/1/drivers/', **self.get_account_header())
        self.assertEqual(response.status_code, 200)
        drivers = response.json()
        self.assertEqual(len(drivers), 2, "Should be the 2 records in test fixtures")
        current_account_company_id = self.get_account().get("company")
        for d in drivers:
            self.assertEqual(d.get("company"), current_account_company_id, "Should be only from users company")
            response = self.client.get(f'/api/1/drivers/{d["id"]}/', **self.get_account_header())
            self.assertEqual(response.status_code, 200, "Should retrieve their drivers")

    def test_drivers_cant_be_get_by_invalid_coordinator(self):
        """
        Invalid: when the coordinator and the driver are not linked to the same company
        Expect: 404 errors when fetching drivers not linked to the same company
        """
        user = User.objects.get(username="c1logistics")
        driver = Driver.objects.get(last_name="C2")
        self.client.force_login(user)
        response = self.client.get(f'/api/1/drivers/{driver.id}/', **self.get_account_header())
        self.assertEqual(response.status_code, 404, "Should not retrieve not companys drivers")

    def test_driver_can_only_be_get_own_driver_record(self):
        """
        Expect: only the record of the driver
        """
        user = User.objects.get(username="c1driver")
        self.client.force_login(user)
        response = self.client.get('/api/1/drivers/', **self.get_account_header())
        self.assertEqual(response.status_code, 200)
        drivers = response.json()
        self.assertEqual(len(drivers), 1, "Should be only the driver record")
        current_account_company_id = self.get_account().get("company")
        for c in drivers:
            self.assertEqual(c.get("company"), current_account_company_id, "Should be from users company")

    def test_driver_cant_get_others_drivers_records(self):
        """
        Expect: only the record of the driver
        """
        user = User.objects.get(username="c1driver")
        driver = Driver.objects.get(last_name="C2")
        self.client.force_login(user)
        response = self.client.get(f'/api/1/drivers/{driver.id}/', **self.get_account_header())
        self.assertEqual(response.status_code, 404, "Should not retrieve others drivers records")

    def test_driver_post_requires_auth_and_valid_account(self):
        """
        Expect: Unauthorized
        """
        company, data = self._get_driver_payload_for_post()

        # not logged in
        response = self.client.post('/api/1/drivers/', data=data)
        self.assertEqual(response.status_code, 403)

    def test_driver_user_cant_post_other_drivers(self):
        """
        Expect: Unauthorized
        """
        company, data = self._get_driver_payload_for_post()

        # logged in without permissions - (a driver)
        user = User.objects.get(username="c1driver")
        self.client.force_login(user)
        response = self.client.post('/api/1/drivers/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 403)

    def test_invalid_account_user_cant_post_drivers(self):
        """
        Invalid: when the user account is not associated with the driver company
        Expect: Unauthorized
        """
        company, data = self._get_driver_payload_for_post()

        # logged in with permissions but not part of user account companies
        user = User.objects.get(username="c2logistics")
        self.client.force_login(user)
        response = self.client.post('/api/1/drivers/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 403)

    def test_driver_can_be_posted_by_coordinator(self):
        """
        Coordinators can post company drivers.
        """
        company, data = self._get_driver_payload_for_post()

        # logged in with permissions and with its user account companies
        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        response = self.client.post('/api/1/drivers/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 201)

        # client created by the user
        new = response.json()
        self.assertEqual(user.id, new['created_by'])

    def test_driver_cant_be_posted_duplicated(self):
        """
        Coordinators can post company drivers but API should avoid duplicates.
        Expect: Validation Errors
        """
        company, data = self._get_driver_payload_for_post()
        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        response = self.client.post('/api/1/drivers/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/api/1/drivers/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 400)
        self.assertTrue('non_field_errors' in response.json(), "Should contain non_field_errors")

    def test_coordinator_can_associate_driver_with_user(self):
        company, data = self._get_driver_payload_for_post()

        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        response = self.client.post('/api/1/drivers/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 201)

        driver = response.json()

        # Validate payloads
        data = {"email": "newtestcom", "company": company.id}
        response = self.client.post(f'/api/1/drivers/{driver["id"]}/user/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 500)

        # associate the user
        data = {"email": "new@test.com", "company": company.id}
        response = self.client.post(f'/api/1/drivers/{driver["id"]}/user/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 200)

        user, account, driver = response.json()["user"], response.json()["account"], response.json()["driver"]
        # user has group drivers
        self.assertTrue(4 in user["groups"], "User must contains the Drivers group")
        self.assertEqual(account["company"], company.id)

    def test_coordinator_cant_associate_driver_from_different_company(self):
        company, data = self._get_driver_payload_for_post()
        data = {"email": "new@test.com", "company": company.id}
        user = User.objects.get(username="c1logistics")
        driver2 = Driver.objects.get(id=2)
        self.client.force_login(user)
        response = self.client.post(f'/api/1/drivers/{driver2.id}/user/', data=data, **self.get_account_header())
        self.assertEqual(response.status_code, 404)

    def test_coordinator_can_edit_company_drivers(self):
        user = User.objects.get(username="c1logistics")
        driver1 = Driver.objects.get(id=1)
        self.client.force_login(user)
        response = self.client.get(f"/api/1/drivers/{driver1.id}/", **self.get_account_header())
        self.assertEqual(response.status_code, 200)
        data_original = response.json()
        patch = {"identification": 9, "company": driver1.company_id}
        response = self.client.patch(f"/api/1/drivers/{driver1.id}/", data=patch,
                                     **self.get_account_header(), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data_patched = response.json()
        self.assertNotEqual(data_original["identification"], data_patched["identification"])

    def test_coordinator_cant_edit_other_companies_drivers(self):
        user = User.objects.get(username="c1logistics")
        driver1 = Driver.objects.get(id=1)
        self.client.force_login(user)
        response = self.client.get(f"/api/1/drivers/{driver1.id}/", **self.get_account_header())
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username="c2logistics")
        self.client.force_login(user)
        patch = {"identification": 9, "company": driver1.company_id}
        response = self.client.patch(f"/api/1/drivers/{driver1.id}/", data=patch,
                                     **self.get_account_header(), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_driver_can_edit_own_record(self):
        driver1 = Driver.objects.get(id=1)
        user = driver1.user
        self.client.force_login(user)
        response = self.client.get(f"/api/1/drivers/{driver1.id}/", **self.get_account_header())
        self.assertEqual(response.status_code, 200)

        patch = {"identification": 9, "company": driver1.company_id}
        response = self.client.patch(f"/api/1/drivers/{driver1.id}/", data=patch,
                                     **self.get_account_header(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_coordinator_can_delete_driver(self):
        company = Company.objects.get(name="C1 Logistics")
        user = User.objects.get(username="c1logistics")
        driver1 = Driver.objects.get(id=1)
        self.client.force_login(user)
        data = {"company": company.id}
        response = self.client.delete(f'/api/1/drivers/{driver1.id}/', data=data,
                                      **self.get_account_header(), content_type='application/json')
        self.assertEqual(response.status_code, 204)

    def test_coordinator_cant_delete_others_companies_driver(self):
        company = Company.objects.get(name="C1 Logistics")
        user = User.objects.get(username="c1logistics")
        driver2 = Driver.objects.get(id=2)
        self.client.force_login(user)
        data = {"company": company.id}
        response = self.client.delete(f'/api/1/drivers/{driver2.id}/', data=data,
                                      **self.get_account_header(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_coordinator_can_get_all_drivers_docs(self):
        company = Company.objects.get(name="C1 Logistics")
        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        response = self.client.get('/api/1/drivers/docs/', **self.get_account_header())
        self.assertEqual(response.status_code, 200)
        docs = response.json()
        for d in docs:
            self.assertEqual(d["company"], company.id, "Should only see companies drivers docs")

    def test_driver_can_get_own_docs(self):
        company1 = Company.objects.get(name="C1 Logistics")
        driver1 = company1.drivers.get(id=1)
        user1 = driver1.user
        self.client.force_login(user1)
        response = self.client.get('/api/1/drivers/docs/', **self.get_account_header())
        for doc in response.json():
            self.assertEqual(driver1.id, doc["driver"])

    def test_driver_docs_post_requires_auth_and_valid_account(self):
        """
        Expect: Unauthorized
        """
        # not logged in
        driver1 = Driver.objects.get(last_name="C1")
        data = self._get_driver_document_payload_for_post(driver1)
        response = self.client.post('/api/1/drivers/docs/', data=data, format="multipart")
        self.assertEqual(response.status_code, 403, "Expected unauthorized")

        # logged in but not part of the company
        user2 = User.objects.get(username="c2logistics")
        self.client.force_login(user2)
        data = self._get_driver_document_payload_for_post(driver1)
        response = self.client.post('/api/1/drivers/docs/', data=data, format="multipart",
                                    **self.get_account_header())
        self.assertEqual(response.status_code, 403, "Expected unauthorized")

        # part of the company but not the driver
        user1 = User.objects.get(username="c1logistics")
        self.client.force_login(user1)
        driver2 = Driver.objects.get(last_name="C2")
        data = self._get_driver_document_payload_for_post(driver2)
        response = self.client.post('/api/1/drivers/docs/', data=data, format="multipart",
                                    **self.get_account_header())
        self.assertEqual(response.status_code, 400)
        # validates driver field
        self.assertTrue('driver' in response.json(), "Expected driver key in validation message")

    def test_coordinator_can_post_driver_docs(self):
        user = User.objects.get(username="c1logistics")
        driver1 = Driver.objects.get(last_name="C1")
        data = self._get_driver_document_payload_for_post(driver1)
        self.client.force_login(user)
        response = self.client.post('/api/1/drivers/docs/', data=data, format="multipart",
                                    **self.get_account_header())
        self.assertEqual(response.status_code, 201)

    def test_driver_can_post_their_docs(self):
        driver1 = Driver.objects.get(last_name="C1")
        user1 = driver1.user
        data = self._get_driver_document_payload_for_post(driver1)
        self.client.force_login(user1)
        response = self.client.post('/api/1/drivers/docs/', data=data, format="multipart",
                                    **self.get_account_header())
        self.assertEqual(response.status_code, 201)

    def test_coordinator_can_delete_driver_docs(self):
        company1 = Company.objects.get(name="C1 Logistics")
        driver1 = Driver.objects.get(last_name="C1")
        docs1 = driver1.docs.all()[0]
        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        data = {"company": company1.id}
        response = self.client.delete(f'/api/1/drivers/docs/{docs1.id}/',
                                      data=data, **self.get_account_header(),
                                      content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_coordinator_cant_delete_other_companies_drivers_docs(self):
        company1 = Company.objects.get(name="C1 Logistics")
        driver2 = Driver.objects.get(last_name="C2")
        docs2 = driver2.docs.all().first()
        user = User.objects.get(username="c1logistics")
        self.client.force_login(user)
        data = {"company": company1.id}
        response = self.client.delete(f'/api/1/drivers/docs/{docs2.id}/',
                                      data=data, **self.get_account_header(),
                                      content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_driver_can_delete_own_doc(self):
        company1 = Company.objects.get(name="C1 Logistics")
        driver1 = company1.drivers.all().first()
        docs1 = driver1.docs.all().first()
        user1 = driver1.user
        self.client.force_login(user1)
        data = {"company": company1.id}
        response = self.client.delete(f'/api/1/drivers/docs/{docs1.id}/',
                                      data=data, **self.get_account_header(),
                                      content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_driver_cant_delete_others_drivers_docs(self):
        company1 = Company.objects.get(name="C1 Logistics")
        driver1 = company1.drivers.all().first()
        user1 = driver1.user

        company2 = Company.objects.get(name="C2 Logistics")
        driver2 = company2.drivers.all().first()
        docs2 = driver2.docs.all().first()
        data = {"company": company1.id}
        self.client.force_login(user1)
        response = self.client.delete(f'/api/1/drivers/docs/{docs2.id}/',
                                      data=data, **self.get_account_header(),
                                      content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_driver_cant_delete_others_drivers_doc_from_same_company(self):
        company1 = Company.objects.get(name="C1 Logistics")
        driver1 = company1.drivers.all().first()
        driver12 = company1.drivers.all().last()
        docs1 = driver1.docs.all().first()
        user12 = driver12.user
        self.client.force_login(user12)
        data = {"company": company1.id}
        response = self.client.delete(f'/api/1/drivers/docs/{docs1.id}/',
                                      data=data, **self.get_account_header(),
                                      content_type="application/json")
        self.assertEqual(response.status_code, 404)
