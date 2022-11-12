# netherite!

## Models

For models you have to take care about:

- Admin
- Serializers, Views and Filters
- Permissions
- Validations
- Signals
- Register activity feed
- Tests

### User

Deinition: user is the people. This model is the backbone for the authenticating system.

### Groups

Deinition: permissions are wrapped into groups, one user belongs to at least one group.

- Superuser
- Coordinators
- Drivers
- Providers (Vehicle Owners)

### Company

Definition: Companies are the core users, they run business processes (logistic operations).

As superuser I can create companies so they can sign-up to the platform.

##### TODO

- names must be unique

### Account

Definition: Association of users vs companies are made through this model.

### Client

Definition: Clients are "Company"s customers.

As coordinator I can CRUD clients.

##### TODO

- names must be unique by company

### Driver

Definition: Drives a vehicle. Drivers should be associated to a user in order to manage their functions in the platform.

As Coordinator I can CRUD drivers. (T)

##### TODO

- drivers identification must be unique by company

#### Asosicate user with driver:

Create driver has 2 steps: 1. Create driver with names and identification and 2. Associate with an User email.

Considerations on created user-based drivers:
The user can be selected from the list of company users, or an email can be typed.

1. Find existing user with that email, or create a new user.
2. Add it to the drivers group.
3. Find existing account for this user and company, or create a new account.
4. Send a notification email of new driver association {notifications}

As Coordinator I can associate an user with any company's driver (T)

### Driver Documents

Definition: Drivers has documents.

- As Driver I can upload my documents (T)
- As Driver I can update or delete own documents. (T)
- As Coordinator I can upload company's drivers documents. (T)
- As Coordinator I can CRUD any of company's drivers documents. (T)

### Vehicle

Definition: A vehicle is a company resource owned by a provider.

- As Coordinator I can CRUD vehicles.

##### TODO

- plates must be unique by client

### Vehicle Documents

Definition: A vehicle has documents

- As Driver associated with this vehicle I can upload documents.

## python dependences

### django-activity-stream

django-activity-stream was installed directly from https://github.com/justquick/django-activity-stream, download zip and
setup.py install.




PERMISSIONS PRIORITY
--------

1. User is logged in (viewset permission)
2. User has group permissions for model action (viewset permission)
3. User has account associated with the header (viewset permission)
4. Model has company associated with the account (viewset validator)

# NEXT:

- ~~filters~~


