import uuid as uuid

from django.conf import settings
from django.db import models

from accounts.models import Company


class Client(models.Model):
    """
    Clients are customers from companies who offer logistic services.
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=255
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        """
        constraints = [
            UniqueConstraint(
                'company',
                Lower('name').desc(),
                name='company_client_name_unique',
            ),
        ]
        """

    def __str__(self):
        return f"{self.name} @ {self.company}"

    def natural_key(self):
        return (self.uuid, self.name)
