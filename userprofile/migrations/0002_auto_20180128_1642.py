# Generated by Django 1.11 on 2018-01-28 15:42
from __future__ import unicode_literals

from django.db import migrations


def create_profiles(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    User = apps.get_model("auth", "User")
    Profile = apps.get_model("userprofile", "Profile")
    for user in User.objects.all():
        Profile.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_profiles),
    ]
