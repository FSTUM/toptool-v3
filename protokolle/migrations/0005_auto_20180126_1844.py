# Generated by Django 1.11 on 2018-01-26 17:44
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("protokolle", "0004_auto_20171001_1355"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="meeting",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="meetings.Meeting",
                verbose_name="Sitzung",
            ),
        ),
    ]
