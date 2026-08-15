from rest_framework import serializers
from .models import GardeningExpense

class GardeningExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GardeningExpense
        fields = ['id', 'title', 'category', 'amount', 'date', 'receipt_image']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("টাকার পরিমাণ ০ এর বেশি হতে হবে।")
        return value
