# Generated by Django 5.1.3 on 2025-03-02 18:37

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityOverview',
            fields=[
                ('activity_id', models.IntegerField(primary_key=True, serialize=False)),
                ('activity_date', models.DateTimeField(verbose_name='activity date')),
                ('activity_name', models.CharField(max_length=120)),
                ('average_hr', models.FloatField(null=True)),
                ('start_lat', models.FloatField(null=True)),
                ('start_lon', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Athlete',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('athlete_id', models.BigIntegerField(unique=True)),
                ('username', models.CharField(max_length=120)),
                ('first_name', models.CharField(max_length=120)),
                ('last_name', models.CharField(max_length=120)),
                ('access_token', models.CharField(max_length=64, unique=True)),
                ('refresh_token', models.CharField(max_length=64, unique=True)),
                ('expires_at', models.DateTimeField(verbose_name='expiration date')),
                ('scope', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='activity timestamp')),
                ('lat', models.FloatField(verbose_name='latitude')),
                ('lon', models.FloatField(verbose_name='longitude')),
                ('heart_rate', models.FloatField(verbose_name='heart rate')),
                ('distance', models.FloatField(verbose_name='distance')),
                ('elevation', models.FloatField(verbose_name='elevation')),
                ('activity_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strivers.activityoverview')),
            ],
        ),
        migrations.AddField(
            model_name='activityoverview',
            name='athlete_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strivers.athlete'),
        ),
    ]
