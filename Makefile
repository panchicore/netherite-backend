test-fixtures:
	python manage.py dumpdata auth.Permission 			--indent 2 > accounts/fixtures/tests/permissions.json
	python manage.py dumpdata auth.Group 				--indent 2 > accounts/fixtures/tests/groups.json
	python manage.py dumpdata auth.User 				--indent 2 --pk 1,2,3,4,5,6 > accounts/fixtures/tests/users.json
	python manage.py dumpdata accounts.Company 			--indent 2 --pk 1,2 > accounts/fixtures/tests/companies.json
	python manage.py dumpdata accounts.Account 			--indent 2 --pk 1,2,3,4,5 > accounts/fixtures/tests/accounts.json
	python manage.py dumpdata clients.Client 			--indent 2 --pk 1,2 > clients/fixtures/tests/clients.json
	python manage.py dumpdata drivers.Driver 			--indent 2 --pk 1,2,3 > drivers/fixtures/tests/drivers.json
	python manage.py dumpdata drivers.DriverDocument 	--indent 2 --pk 1,2,3 > drivers/fixtures/tests/drivers_docs.json


load-initial-data:
	python manage.py loaddata accounts/fixtures/tests/groups.json
	python manage.py loaddata accounts/fixtures/tests/users.json
	python manage.py loaddata accounts/fixtures/tests/companies.json
	python manage.py loaddata accounts/fixtures/tests/accounts.json
	python manage.py loaddata clients/fixtures/tests/clients.json
	python manage.py loaddata drivers/fixtures/tests/drivers.json
	python manage.py loaddata drivers/fixtures/tests/drivers_docs.json

test:
	python manage.py test
