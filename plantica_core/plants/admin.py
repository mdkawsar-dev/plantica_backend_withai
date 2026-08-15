from django.contrib import admin
from .models import MasterPlant, Plant, PlantTask

@admin.register(MasterPlant)
class MasterPlantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_bn', 'name_en', 'scientific_name', 'category')
    search_fields = ('name_bn', 'name_en', 'scientific_name')
    list_filter = ('category',)

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nickname', 'species', 'planting_date', 'location', 'age_display')
    search_fields = ('nickname', 'species', 'user__username')
    list_filter = ('location', 'species')

@admin.register(PlantTask)
class PlantTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plant', 'task_type', 'due_date', 'due_time', 'repeat_frequency', 'is_completed')
    search_fields = ('plant__nickname', 'user__username', 'task_type')
    list_filter = ('is_completed', 'task_type', 'repeat_frequency')
