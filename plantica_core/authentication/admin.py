from django.contrib import admin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'role', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('role', 'is_staff')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'gardening_type', 'address')
    search_fields = ('user__username', 'address')
