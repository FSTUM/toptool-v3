# Generated by Django 1.11 on 2018-02-12 17:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetingtypes", "0013_meetingtype_top_perms"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingtype",
            name="tops",
            field=models.BooleanField(
                default=True,
                verbose_name="Tagesordnung verwenden",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="meetingtype",
            name="top_perms",
            field=models.CharField(
                choices=[
                    (
                        "admin",
                        "Nur Sitzungsgruppen-Admins und Sitzungsleitung können TOPs eintragen",
                    ),
                    (
                        "perm",
                        "Nur Benutzer mit Rechten für die Sitzungsgruppen können TOPs eintragen",
                    ),
                    (
                        "public",
                        "Alle, auch nicht eingeloggte Benutzer, können TOPs eintragen "
                        "(nur relevant, wenn Sitzungsgruppe öffentlich ist)",
                    ),
                ],
                max_length=10,
                verbose_name="Rechte für das Eintragen von TOPs",
            ),
        ),
    ]
