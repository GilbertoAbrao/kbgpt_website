# Generated by Django 4.2.3 on 2023-07-17 22:29

from django.db import migrations, models
import kbgpt_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('kbgpt_app', '0009_botmodel_group'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='botfilesmodel',
            options={'verbose_name': 'BotFile', 'verbose_name_plural': 'BotsFiles'},
        ),
        migrations.RemoveField(
            model_name='botfilesmodel',
            name='file_id',
        ),
        migrations.AddField(
            model_name='botfilesmodel',
            name='name',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='botfilesmodel',
            name='path',
            field=models.FileField(default=None, upload_to=kbgpt_app.models.user_directory_path),
            preserve_default=False,
        ),
    ]
