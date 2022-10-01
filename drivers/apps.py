from django.apps import AppConfig


class DriversConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'drivers'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Driver'))
