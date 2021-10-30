# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-01 08:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetingtypes", "0004_meetingtype_attachment_tops"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingtype",
            name="attachment_protokoll",
            field=models.BooleanField(
                default=False,
                verbose_name="Anhänge zum Protokoll",
            ),
            preserve_default=False,
        ),
    ]
