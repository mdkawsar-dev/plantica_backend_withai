from django.contrib import admin
from .models import GardeningTask

@admin.register(GardeningTask)
class GardeningTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_plant', 'task_type', 'scheduled_at', 'is_completed')
    list_filter = ('task_type', 'is_completed')
