# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-01 11:55
from __future__ import unicode_literals

from django.db import migrations, models

import protokolle.models
import toptool.shortcuts


class Migration(migrations.Migration):

    dependencies = [
        ("protokolle", "0003_auto_20171001_1052"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="attachment",
            field=models.FileField(
                storage=protokolle.models.AttachmentStorage(),
                upload_to=protokolle.models.attachment_path,
                validators=[toptool.shortcuts.validate_file_type],
                verbose_name="Anhang",
            ),
        ),
    ]
