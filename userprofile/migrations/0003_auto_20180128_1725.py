# Generated by Django 1.11 on 2018-01-28 16:25
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0002_auto_20180128_1642"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="color",
            field=models.CharField(blank=True, max_length=6, verbose_name="Farbe"),
        ),
        migrations.AlterField(
            model_name="profile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Benutzer",
            ),
        ),
    ]
