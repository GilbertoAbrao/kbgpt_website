from django.contrib import admin

from .models import BotModel, ClientModel, FileModel


@admin.register(BotModel)
class BotAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'owner_id')
