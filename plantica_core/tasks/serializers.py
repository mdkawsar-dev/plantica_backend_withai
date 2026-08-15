from rest_framework import serializers
from .models import GardeningTask
from plants.serializers import UserPlantSerializer

class GardeningTaskSerializer(serializers.ModelSerializer):
    plant_details = UserPlantSerializer(source='user_plant', read_only=True)

    class Meta:
        model = GardeningTask
        fields = ['id', 'user', 'user_plant', 'plant_details', 'task_type', 'scheduled_at', 'is_completed', 'repeat_days']
        read_only_fields = ['user']
