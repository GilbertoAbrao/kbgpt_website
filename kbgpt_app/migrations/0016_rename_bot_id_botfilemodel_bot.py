# Generated by Django 4.2.3 on 2023-07-29 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kbgpt_app', '0015_botfilemodel_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='botfilemodel',
            old_name='bot_id',
            new_name='bot',
        ),
    ]
