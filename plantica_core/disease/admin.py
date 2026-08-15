from django.contrib import admin
from .models import DiseaseInfo, DiseaseDiagnosisLog

@admin.register(DiseaseInfo)
class DiseaseInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_index', 'disease_name_bn', 'disease_name_en', 'plant', 'risk_level')
    search_fields = ('disease_name_bn', 'disease_name_en')
    list_filter = ('risk_level', 'plant')

@admin.register(DiseaseDiagnosisLog)
class DiseaseDiagnosisLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_plant', 'predicted_disease', 'confidence_score', 'created_at')
    list_filter = ('is_confirmed_by_user', 'created_at')
