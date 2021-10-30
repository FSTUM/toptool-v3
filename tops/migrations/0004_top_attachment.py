# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-20 08:22
from __future__ import unicode_literals

from django.db import migrations, models

import tops.models


class Migration(migrations.Migration):

    dependencies = [
        ("tops", "0003_auto_20160602_1656"),
    ]

    operations = [
        migrations.AddField(
            model_name="top",
            name="attachment",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=tops.models.attachment_path,
                verbose_name="Anhang",
            ),
        ),
    ]
