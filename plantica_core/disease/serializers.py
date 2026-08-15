from rest_framework import serializers
from .models import DiseaseInfo, DiseaseDiagnosisLog

class DiseaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiseaseInfo
        fields = '__all__'


class DiseaseDiagnosisLogSerializer(serializers.ModelSerializer):
    disease_details = DiseaseInfoSerializer(source='predicted_disease', read_only=True)

    class Meta:
        model = DiseaseDiagnosisLog
        fields = [
            'id', 'user', 'user_plant', 'uploaded_image',
            'predicted_disease', 'disease_details', 'confidence_score',
            'is_confirmed_by_user', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']
