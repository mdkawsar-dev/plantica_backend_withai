from rest_framework import serializers
from .models import MarketplaceListing

class MarketplaceListingSerializer(serializers.ModelSerializer):
    seller_name = serializers.ReadOnlyField(source='seller.first_name')
    seller_phone = serializers.ReadOnlyField(source='seller.phone')

    class Meta:
        model = MarketplaceListing
        fields = [
            'id', 
            'seller', 
            'seller_name', 
            'seller_phone', 
            'title', 
            'category', 
            'price', 
            'quantity', 
            'description', 
            'contact_number', 
            'location', 
            'image', 
            'is_sold', 
            'created_at'
        ]
        read_only_fields = ['seller', 'created_at']
