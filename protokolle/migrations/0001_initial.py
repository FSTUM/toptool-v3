# Generated by Django 1.9 on 2016-03-06 15:59
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import protokolle.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("meetings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Protokoll",
            fields=[
                (
                    "meeting",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="meetings.Meeting",
                        verbose_name="Sitzung",
                    ),
                ),
                ("begin", models.TimeField(verbose_name="Beginn der Sitzung")),
                ("end", models.TimeField(verbose_name="Ende der Sitzung")),
                ("approved", models.BooleanField(verbose_name="genehmigt")),
                (
                    "t2t",
                    models.FileField(
                        upload_to=protokolle.models.protokoll_path,
                        verbose_name="Protokoll",
                    ),
                ),
            ],
        ),
    ]
