# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-10 10:22
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetingtypes", "0006_auto_20180210_1122"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("userprofile", "0004_auto_20180128_1726"),
    ]

    operations = [
        migrations.CreateModel(
            name="MeetingTypePreference",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sortid", models.IntegerField(verbose_name="Sort-ID")),
                (
                    "meetingtype",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meetingtypes.MeetingType",
                        verbose_name="Sitzungsgruppe",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Benutzer",
                    ),
                ),
            ],
        ),
    ]