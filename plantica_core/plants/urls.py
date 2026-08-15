from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlantListCreateView, 
    PlantDropdownListView, 
    TaskListCreateView, 
    ToggleTaskCompleteView,
    MasterPlantViewSet,
    HomeCareSummaryView,
    WeatherForecastView,
    SmartPlantFilterView,
    DistrictPlantRecommendationDetailView,
    UserPlantDetailView,
    SearchNearbyNurseriesView,
    NurseryDetailView
)

router = DefaultRouter()
router.register(r'master-plants', MasterPlantViewSet, basename='master-plant')

urlpatterns = [
    # 1 & 3. My Plants List (GET) & Add New Plant (POST)
    path('', PlantListCreateView.as_view(), name='plant_list_create'),
    
    # User Plant Individual Detail API (Screen 5)
    path('<int:pk>/details/', UserPlantDetailView.as_view(), name='plant_details'),
    path('user-plants/<int:pk>/details/', UserPlantDetailView.as_view(), name='user_plant_details'),
    
    # 4. Minimal Dropdown Plant List (GET)
    path('dropdown/', PlantDropdownListView.as_view(), name='plant_dropdown'),
    
    # 2 & 4. Today's Tasks List (GET) & Create Task (POST)
    path('tasks/', TaskListCreateView.as_view(), name='task_list_create'),
    
    # Home Dashboard Care Summary API
    path('home-summary/', HomeCareSummaryView.as_view(), name='home_care_summary'),
    
    # Weather & 7-Day Forecast API
    path('weather/', WeatherForecastView.as_view(), name='weather_forecast'),

    # Smart Plant Recommendation Filter & Detail APIs
    path('recommendations/search/', SmartPlantFilterView.as_view(), name='smart_plant_search'),
    path('recommendations/<int:pk>/', DistrictPlantRecommendationDetailView.as_view(), name='recommendation_detail'),

    # Nearby Nursery Search & Detail APIs (Google Places Integration)
    path('nurseries/search/', SearchNearbyNurseriesView.as_view(), name='search_nearby_nurseries'),
    path('nurseries/<str:place_id>/details/', NurseryDetailView.as_view(), name='nursery_detail'),
    
    # 2. Task Checkmark Status Toggle (PATCH)
    path('tasks/<int:pk>/toggle/', ToggleTaskCompleteView.as_view(), name='toggle_task'),
    
    path('', include(router.urls)),
]


