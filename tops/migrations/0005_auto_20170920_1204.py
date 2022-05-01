# Generated by Django 1.11.2 on 2017-09-20 10:04
from __future__ import unicode_literals

from django.db import migrations, models

from tops.models import attachment_path
from toptool.utils.files import validate_file_type


class Migration(migrations.Migration):
    dependencies = [
        ("tops", "0004_top_attachment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="top",
            name="attachment",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=attachment_path,
                validators=[validate_file_type],
                verbose_name="Anhang",
            ),
        ),
    ]
