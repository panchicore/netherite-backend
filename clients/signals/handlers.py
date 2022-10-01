from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from actstream import action

from accounts.models import Account
from clients.models import Client


@receiver(pre_save, sender=Client)
def client_pre_save(sender, instance, **kwargs):
    if not Account.objects.is_associated(instance.created_by, instance.company):
        raise ValueError(f"Company '{instance.company}' not associated with any '{instance.created_by}' accounts")


@receiver(post_save, sender=Client)
def client_post_save(sender, instance, created, **kwargs):
    if created:
        action.send(instance.created_by, verb='created', action_object=instance, target=instance.company)
    else:
        action.send(instance.created_by, verb='updated', action_object=instance, target=instance.company)
