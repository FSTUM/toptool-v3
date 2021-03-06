# Generated by Django 1.11 on 2018-07-22 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetingtypes", "0016_meetingtype_pad_setting"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingtype",
            name="anonymous_tops",
            field=models.BooleanField(
                default=False,
                verbose_name="Anonyme TOPs (ohne Name und E-Mail-Adresse) ermöglichen",
            ),
            preserve_default=False,
        ),
    ]
