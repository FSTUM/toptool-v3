# Generated by Django 1.11 on 2018-02-12 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetingtypes", "0011_meetingtype_standard_tops"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingtype",
            name="top_deadline",
            field=models.BooleanField(
                default=True,
                verbose_name="Deadline zum Eintragen von TOPs verwenden",
            ),
            preserve_default=False,
        ),
    ]
