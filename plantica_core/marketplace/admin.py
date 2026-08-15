from django.contrib import admin
from .models import MarketplaceListing

@admin.register(MarketplaceListing)
class MarketplaceListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'seller', 'category', 'price', 'is_sold', 'created_at')
    list_filter = ('category', 'is_sold')
