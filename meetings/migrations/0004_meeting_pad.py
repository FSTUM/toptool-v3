# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-21 13:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0003_meeting_imported"),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="pad",
            field=models.CharField(blank=True, max_length=200, verbose_name="Pad-Name"),
        ),
    ]