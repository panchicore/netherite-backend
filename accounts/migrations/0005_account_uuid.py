# Generated by Django 4.1 on 2022-08-16 20:59

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_company_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
        ),
    ]
