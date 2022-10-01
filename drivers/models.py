import uuid as uuid

from django.conf import settings
from django.db import models

from accounts.models import Company


class Driver(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='drivers'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    first_name = models.CharField(
        max_length=255
    )
    last_name = models.CharField(
        max_length=255
    )
    identification_type = models.CharField(
        max_length=255,
        choices=[
            ('national-id', 'cedula'),
            ('passport', 'passport'),
            ('foreign-id', 'foreign id'),
        ]
    )
    identification = models.CharField(
        max_length=255
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_drivers'
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
                Lower('identification').desc(),
                'company',
                'identification_type',
                name='company_driver_identification_unique',
            ),
        ]
        """

    def __str__(self):
        return f"{self.first_name} {self.last_name} - driver @ {self.company}"

    def notify_to_driver_user(self):
        return True


def driver_directory_path(instance, filename):
    return 'driver/{0}/docs/{1}'.format(instance.driver.id, filename)


class DriverDocument(models.Model):
    IDENTIFICATION = 'identification'
    LICENCE = 'licence'
    OTHER = 'other'
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='driver_docs'
    )
    driver = models.ForeignKey(
        Driver, related_name="docs", on_delete=models.CASCADE
    )
    type = models.CharField(
        choices=[
            (IDENTIFICATION, 'identification'),
            (LICENCE, 'licence'),
            (OTHER, 'other')
        ],
        max_length=100
    )
    file = models.FileField(
        upload_to=driver_directory_path
    )
    expiration_date = models.DateField(
        null=True, blank=True
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

    def __str__(self):
        return f"{self.driver} > {self.get_type_display()}"
