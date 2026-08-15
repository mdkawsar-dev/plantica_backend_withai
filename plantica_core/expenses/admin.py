from django.contrib import admin
from .models import GardeningExpense

@admin.register(GardeningExpense)
class GardeningExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'category', 'amount', 'date')
    list_filter = ('category', 'date')
