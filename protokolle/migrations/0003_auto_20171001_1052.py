# Generated by Django 1.11.2 on 2017-10-01 08:52
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


def change_foreignkey(apps, schema_editor):
    # We can't import the model directly as it may be a newer
    # version than this migration expects. We use the historical
    # version.
    Attachment = apps.get_model("protokolle", "Attachment")
    for attachment in Attachment.objects.all():
        attachment.meeting = attachment.protokoll.meeting
        attachment.save()


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0003_meeting_imported"),
        ("protokolle", "0002_attachment"),
    ]

    operations = [
        migrations.AddField(
            model_name="attachment",
            name="meeting",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="meetings.Meeting",
                verbose_name="Meeting",
                null=True,
            ),
        ),
        migrations.RunPython(change_foreignkey),
        migrations.RemoveField(
            model_name="attachment",
            name="protokoll",
        ),
        migrations.AlterField(
            model_name="attachment",
            name="meeting",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="meetings.Meeting",
                verbose_name="Meeting",
            ),
        ),
    ]
