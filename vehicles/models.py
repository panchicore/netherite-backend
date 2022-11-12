import uuid as uuid

from django.conf import settings
from django.db import models

from accounts.models import Company


def vehicle_document_directory_path(instance, filename):
    return 'vehicle/{0}/docs/{1}'.format(instance.vehicle.id, filename)


class VehicleType(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='vehicle_types'
    )
    name = models.CharField(
        max_length=255
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_vehicle_types'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"<{self.company}> vehicle type <{self.name}>"


class Vehicle(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='vehicles'
    )
    type = models.ForeignKey(
        VehicleType,
        on_delete=models.CASCADE
    )
    plate = models.CharField(
        max_length=100
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_vehicles'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"<{self.company}> vehicle <{self.type}> {self.plate}"


class VehicleDocument(models.Model):
    IDENTIFICATION = 'identification'
    LICENCE = 'licence'
    SOAT = 'soat'
    RTM = 'rtm'
    OTHER = 'other'
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='vehicle_documents'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE
    )
    type = models.CharField(
        choices=[
            (IDENTIFICATION, IDENTIFICATION),
            (LICENCE, LICENCE),
            (SOAT, SOAT),
            (RTM, RTM),
            (OTHER, OTHER)
        ],
        max_length=100
    )
    file = models.FileField(
        upload_to=vehicle_document_directory_path
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
        return f"{self.vehicle} document <{self.type}>"
