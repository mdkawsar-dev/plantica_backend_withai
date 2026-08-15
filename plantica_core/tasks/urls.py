from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GardeningTaskViewSet

router = DefaultRouter()
router.register(r'gardening-tasks', GardeningTaskViewSet, basename='gardening-task')

urlpatterns = [
    path('', include(router.urls)),
]
