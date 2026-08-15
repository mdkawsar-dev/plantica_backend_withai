from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DiseaseInfoViewSet, 
    DiseaseDiagnosisLogViewSet, 
    DiseaseDetectionView, 
    DiseaseDetectionAiView, 
    DiseaseDetectionMlView
)

router = DefaultRouter()
router.register(r'info', DiseaseInfoViewSet, basename='disease-info')
router.register(r'scans', DiseaseDiagnosisLogViewSet, basename='disease-scan')

urlpatterns = [
    path('', include(router.urls)),
    # 🆕 Unified Endpoint (supports mode='ai' or mode='ml')
    path('detect/', DiseaseDetectionView.as_view(), name='disease_detect'),
    # 🆕 Direct AI Vision Endpoint
    path('detect/ai/', DiseaseDetectionAiView.as_view(), name='disease_detect_ai'),
    # 🆕 Direct Kaggle ML Model Endpoint
    path('detect/ml/', DiseaseDetectionMlView.as_view(), name='disease_detect_ml'),
]
