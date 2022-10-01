import uuid as uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from accounts.managers import AccountManager


class Company(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    name = models.CharField(
        max_length=255
    )

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.uuid, self.name


class Account(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True,
        db_index=True
    )
    company = models.ForeignKey(
        Company,
        related_name="accounts",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts"
    )

    objects = AccountManager()

    def __str__(self):
        return f"{self.user} @ {self.company}"

    def natural_key(self):
        return self.uuid, self.company.name
