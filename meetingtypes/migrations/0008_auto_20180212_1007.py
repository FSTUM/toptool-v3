# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-12 09:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetingtypes", "0007_auto_20180212_0858"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingtype",
            name="motion_tag",
            field=models.BooleanField(
                default=True,
                verbose_name="Kurze Syntax für Anträge im Protokoll verwenden",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="meetingtype",
            name="point_of_order_tag",
            field=models.BooleanField(
                default=True,
                verbose_name="Kurze Syntax für GO-Anträge im Protokoll verwenden",
            ),
            preserve_default=False,
        ),
    ]