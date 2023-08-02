import os
import uuid
import random
from datetime import datetime 
from django.db import models
from django.contrib.auth.models import User, Group


def user_directory_path(instance, filename):
    # Get Current Date
    # todays_date = datetime.now()
    # path = "uploads/{}/{}/{}/".format(todays_date.year, todays_date.month, todays_date.day)

    path = f"uploads/bots_files/{instance.bot.owner.username}/{str(instance.bot.uuid)}/"
    extension = "." + filename.split('.')[-1]

    # Filename reformat
    filename_reformat = str(instance.uuid) + extension

    return os.path.join(path, filename_reformat)



class ClientModel(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clients"
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name



class BotModel(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bots"
        verbose_name = "Bot"
        verbose_name_plural = "Bots"

    def __str__(self):
        return self.name



class BotFileModel(models.Model):
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('error', 'Error'),
    )

    bot = models.ForeignKey(BotModel, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    path = models.FileField(upload_to=user_directory_path)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='processing')
    callback_url = models.CharField(max_length=255, null=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bots_files"
        verbose_name = "BotFile"
        verbose_name_plural = "BotsFiles"

    def __str__(self):
        return self.name



class FileModel(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.CharField(max_length=255, null=True, blank=True)
    path = models.FileField(upload_to=user_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bot_id = models.ForeignKey(BotModel, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "files"
        verbose_name = "File"
        verbose_name_plural = "Files"

    def __str__(self):
        return self.name


