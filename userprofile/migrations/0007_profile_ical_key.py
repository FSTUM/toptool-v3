# Generated by Django 1.11 on 2018-02-12 14:17
from __future__ import unicode_literals

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0006_auto_20180210_1141"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="ical_key",
            field=models.UUIDField(default=uuid.uuid4, verbose_name="iCal-Key"),
        ),
    ]
