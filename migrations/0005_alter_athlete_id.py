# Generated by Django 5.1.4 on 2025-01-19 17:47

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strivers', '0004_athlete_first_name_athlete_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athlete',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
