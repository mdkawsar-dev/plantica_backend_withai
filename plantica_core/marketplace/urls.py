from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MarketplaceProductListView,
    MyListingsView,
    MarketplaceProductDetailView,
    MarkStockoutView,
    MarketplaceListingViewSet
)

router = DefaultRouter()
router.register(r'listings', MarketplaceListingViewSet, basename='marketplace-listing')

urlpatterns = [
    # Feed, Search, Category Filter & Create Listing API
    path('products/', MarketplaceProductListView.as_view(), name='marketplace_products'),
    
    # My Listings API
    path('my-listings/', MyListingsView.as_view(), name='my_listings'),
    
    # Product Edit (PUT/PATCH) & Delete (DELETE) API
    path('products/<int:pk>/', MarketplaceProductDetailView.as_view(), name='product_detail'),
    
    # Mark Stockout / Sold Out Toggle API
    path('products/<int:pk>/stockout/', MarkStockoutView.as_view(), name='mark_stockout'),
    
    path('', include(router.urls)),
]
