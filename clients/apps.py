from django.apps import AppConfig
from django.db.models.signals import pre_save


class ClientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clients'

    def ready(self):
        from clients.signals import handlers

        from actstream import registry
        registry.register(self.get_model('Client'))
