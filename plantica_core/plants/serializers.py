from rest_framework import serializers
from .models import Plant, PlantTask, MasterPlant, DistrictPlantRecommendation
from disease.models import DiseaseDiagnosisLog

class MasterPlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterPlant
        fields = ['id', 'name_bn', 'name_en', 'scientific_name', 'category', 'image', 'description', 'suitable_sunlight', 'suitable_season']


# --- 1. Plant List & Create Serializer ---
class PlantSerializer(serializers.ModelSerializer):
    age_display = serializers.ReadOnlyField()

    class Meta:
        model = Plant
        fields = ['id', 'nickname', 'species', 'planting_date', 'location', 'image', 'age_display']


UserPlantSerializer = PlantSerializer


# --- 2. Plant Dropdown Serializer ---
class PlantDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ['id', 'nickname', 'species', 'image']


# --- 3. Plant Task Serializer ---
class PlantTaskSerializer(serializers.ModelSerializer):
    plant_name = serializers.ReadOnlyField(source='plant.nickname')
    plant_image = serializers.SerializerMethodField()

    class Meta:
        model = PlantTask
        fields = [
            'id', 
            'plant', 
            'plant_name', 
            'plant_image', 
            'task_type', 
            'due_date', 
            'due_time', 
            'repeat_frequency', 
            'is_completed', 
            'completed_at'
        ]

    def get_plant_image(self, obj):
        request = self.context.get('request')
        if obj.plant.image and request:
            return request.build_absolute_uri(obj.plant.image.url)
        return None


# --- 4. Task Summary Serializer (For Plant Details) ---
class TaskSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantTask
        fields = ['id', 'task_type', 'due_date', 'due_time', 'repeat_frequency', 'is_completed', 'completed_at']


# --- 5. Plant Disease Report Serializer ---
class PlantDiseaseReportSerializer(serializers.ModelSerializer):
    disease_name_bn = serializers.SerializerMethodField()
    disease_name_en = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()
    treatment = serializers.SerializerMethodField()

    class Meta:
        model = DiseaseDiagnosisLog
        fields = [
            'id',
            'disease_name_bn',
            'disease_name_en',
            'confidence_score',
            'uploaded_image',
            'risk_level',
            'treatment',
            'created_at'
        ]

    def get_disease_name_bn(self, obj):
        if obj.predicted_disease:
            return obj.predicted_disease.disease_name_bn
        return "সুস্থ / কোন রোগ সনাক্ত হয়নি"

    def get_disease_name_en(self, obj):
        if obj.predicted_disease:
            return obj.predicted_disease.disease_name_en
        return "Healthy / No Disease Detected"

    def get_risk_level(self, obj):
        if obj.predicted_disease:
            return obj.predicted_disease.risk_level
        return "low"

    def get_treatment(self, obj):
        if obj.predicted_disease:
            return obj.predicted_disease.treatment_bn
        return "নিয়মিত সঠিক পরিচর্যা ও সূর্যালোক বজায় রাখুন।"


# --- 6. District Plant Recommendation Serializer ---
class DistrictPlantRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictPlantRecommendation
        fields = '__all__'

