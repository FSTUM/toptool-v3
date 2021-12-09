# Generated by Django 3.2.9 on 2021-12-09 20:33

from django.db import migrations, models
import protokolle.models
import toptool.utils.files


class Migration(migrations.Migration):

    dependencies = [
        ('protokolle', '0007_protokoll_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='attachment',
            field=models.FileField(help_text='Erlaubte Dateiformate: pdf, ods, xlsx, png, jpg, jpeg', storage=protokolle.models.AttachmentStorage(), upload_to=protokolle.models.attachment_path, validators=[toptool.utils.files.validate_file_type], verbose_name='Anhang'),
        ),
    ]
