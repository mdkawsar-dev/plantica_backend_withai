from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from authentication.views import (
    LoginView, LogoutView, RegisterView, ForgotPasswordEmailView, OTPVerifyView, ResetPasswordView,
    UserProfileView, UserProfileUpdateView
)
from marketplace.views import (
    MarketplaceProductListView, MyListingsView, MarketplaceProductDetailView, MarkStockoutView
)
from community.views import (
    CommunityPostListView, CommunityPostDetailView, PostLikeToggleView, AddCommentView, AddReplyCommentView, CommunityHighlightView
)
from plants.views import (
    PlantListCreateView, PlantDropdownListView, TaskListCreateView, ToggleTaskCompleteView, HomeCareSummaryView, WeatherForecastView, SmartPlantFilterView, DistrictPlantRecommendationDetailView, UserPlantDetailView, SearchNearbyNurseriesView, NurseryDetailView
)
from notifications.views import (
    NotificationCenterView, MarkSingleNotificationReadView, MarkAllNotificationsReadView
)
from disease.views import DiseaseDetectionView, DiseaseDetectionAiView, DiseaseDetectionMlView
from ai_assistant.views import (
    AiChatView, AiChatHistoryView, AiConversationListView, AiVoiceAssistantView
)
from plantica_core.responses import success_response

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root_view(request):
    return success_response(
        data={
            "app_name": "Plantica Core API",
            "version": "v1",
            "status": "Online",
            "endpoints": {
                "admin": "/admin/",
                "login": "/api/v1/auth/login/",
                "logout": "/api/v1/auth/logout/",
                "register": "/api/v1/auth/register/",
                "get_profile": "/api/v1/auth/profile/",
                "update_profile": "/api/v1/auth/profile/update/",
                "recommendation_search": "/api/v1/plants/recommendations/search/",
                "recommendation_detail": "/api/v1/plants/recommendations/<id>/",
                "nursery_search": "/api/v1/plants/nurseries/search/",
                "nursery_detail": "/api/v1/plants/nurseries/<place_id>/details/",
                "notifications": "/api/v1/notifications/",
                "notifications_read_all": "/api/v1/notifications/read-all/",
                "notifications_single_read": "/api/v1/notifications/<id>/read/",
                "home_care_summary": "/api/v1/plants/home-summary/",
                "weather_forecast": "/api/v1/plants/weather/",
                "my_plants": "/api/v1/plants/",
                "user_plant_details": "/api/v1/plants/<id>/details/",
                "plant_dropdown": "/api/v1/plants/dropdown/",
                "today_tasks": "/api/v1/plants/tasks/",
                "create_task": "/api/v1/plants/tasks/",
                "toggle_task": "/api/v1/plants/tasks/<id>/toggle/",
                "community_feed": "/api/v1/community/posts/",
                "community_highlights": "/api/v1/community/posts/highlights/",
                "post_detail": "/api/v1/community/posts/<id>/",
                "post_like_toggle": "/api/v1/community/posts/<id>/like/",
                "add_comment": "/api/v1/community/posts/<id>/comments/",
                "add_reply": "/api/v1/community/comments/<comment_id>/reply/",
                "marketplace_feed": "/api/v1/marketplace/products/",
                "my_listings": "/api/v1/marketplace/my-listings/",
                "product_detail_edit_delete": "/api/v1/marketplace/products/<id>/",
                "mark_stockout": "/api/v1/marketplace/products/<id>/stockout/",
                "expense_summary": "/api/v1/expenses/summary/",
                "add_expense": "/api/v1/expenses/add/",
                "forgot_password_send_otp": "/api/v1/auth/forgot-password/send-otp/",
                "forgot_password_verify_otp": "/api/v1/auth/forgot-password/verify-otp/",
                "forgot_password_reset": "/api/v1/auth/forgot-password/reset/",
                "token_refresh": "/api/v1/auth/token/refresh/",
                "auth": "/api/v1/auth/",
                "plants": "/api/v1/plants/",
                "disease": "/api/v1/disease/",
                "disease_detect": "/api/v1/disease/detect/",
                "disease_detect_ai": "/api/v1/disease/detect/ai/",
                "disease_detect_ml": "/api/v1/disease/detect/ml/",
                "tasks": "/api/v1/tasks/",
                "community": "/api/v1/community/",
                "marketplace": "/api/v1/marketplace/",
                "expenses": "/api/v1/expenses/",
                "notifications": "/api/v1/notifications/"
            }
        },
        message="Welcome to Plantica Core API Service"
    )

urlpatterns = [
    path('', api_root_view, name='api_root'),
    path('admin/', admin.site.urls),
    
    # Direct Auth Shortcuts
    path('api/v1/auth/login/', LoginView.as_view(), name='auth_login'),
    path('api/v1/auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/v1/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/v1/auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('api/v1/auth/profile/update/', UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('api/v1/auth/forgot-password/send-otp/', ForgotPasswordEmailView.as_view(), name='forgot_password_send_otp'),
    path('api/v1/auth/forgot-password/verify-otp/', OTPVerifyView.as_view(), name='forgot_password_verify_otp'),
    path('api/v1/auth/forgot-password/reset/', ResetPasswordView.as_view(), name='forgot_password_reset'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Direct Dashboard, Weather, Recommendation & Nursery Shortcuts
    path('api/v1/plants/home-summary/', HomeCareSummaryView.as_view(), name='home_care_summary'),
    path('api/v1/plants/weather/', WeatherForecastView.as_view(), name='weather_forecast'),
    path('api/v1/plants/recommendations/search/', SmartPlantFilterView.as_view(), name='smart_plant_search'),
    path('api/v1/plants/recommendations/<int:pk>/', DistrictPlantRecommendationDetailView.as_view(), name='recommendation_detail'),
    path('api/v1/plants/nurseries/search/', SearchNearbyNurseriesView.as_view(), name='search_nearby_nurseries'),
    path('api/v1/plants/nurseries/<str:place_id>/details/', NurseryDetailView.as_view(), name='nursery_detail'),

    # Direct Plants & Tasks Shortcuts
    path('api/v1/plants/', PlantListCreateView.as_view(), name='plant_list_create'),
    path('api/v1/plants/<int:pk>/details/', UserPlantDetailView.as_view(), name='plant_details'),
    path('api/v1/plants/user-plants/<int:pk>/details/', UserPlantDetailView.as_view(), name='user_plant_details'),
    path('api/v1/plants/dropdown/', PlantDropdownListView.as_view(), name='plant_dropdown'),
    path('api/v1/plants/tasks/', TaskListCreateView.as_view(), name='task_list_create'),
    path('api/v1/plants/tasks/<int:pk>/toggle/', ToggleTaskCompleteView.as_view(), name='toggle_task'),

    # Direct Marketplace Shortcuts
    path('api/v1/marketplace/products/', MarketplaceProductListView.as_view(), name='marketplace_products'),
    path('api/v1/marketplace/my-listings/', MyListingsView.as_view(), name='my_listings'),
    path('api/v1/marketplace/products/<int:pk>/', MarketplaceProductDetailView.as_view(), name='product_detail'),
    path('api/v1/marketplace/products/<int:pk>/stockout/', MarkStockoutView.as_view(), name='mark_stockout'),
    
    # Direct Community Shortcuts
    path('api/v1/community/posts/', CommunityPostListView.as_view(), name='post_list_create'),
    path('api/v1/community/posts/highlights/', CommunityHighlightView.as_view(), name='community_highlights'),
    path('api/v1/community/posts/<int:pk>/', CommunityPostDetailView.as_view(), name='post_detail'),
    path('api/v1/community/posts/<int:pk>/like/', PostLikeToggleView.as_view(), name='post_like_toggle'),
    path('api/v1/community/posts/<int:pk>/comments/', AddCommentView.as_view(), name='add_comment'),
    path('api/v1/community/comments/<int:comment_id>/reply/', AddReplyCommentView.as_view(), name='add_reply'),

    # Direct Notifications Shortcuts
    path('api/v1/notifications/', NotificationCenterView.as_view(), name='notification_list'),
    path('api/v1/notifications/read-all/', MarkAllNotificationsReadView.as_view(), name='mark_all_read'),
    path('api/v1/notifications/<int:pk>/read/', MarkSingleNotificationReadView.as_view(), name='mark_single_read'),

    # 🆕 AI Disease Detection Direct Shortcuts
    path('api/v1/disease/detect/', DiseaseDetectionView.as_view(), name='disease_detect'),
    path('api/v1/disease/detect/ai/', DiseaseDetectionAiView.as_view(), name='disease_detect_ai'),
    path('api/v1/disease/detect/ml/', DiseaseDetectionMlView.as_view(), name='disease_detect_ml'),

    # 🆕 AI Chat & Voice Assistant Direct Shortcuts
    path('api/chat/send', AiChatView.as_view(), name='legacy_chat_send'),
    path('api/chat/list', AiConversationListView.as_view(), name='legacy_chat_list'),
    path('api/chat/get/<uuid:conversation_id>', AiChatHistoryView.as_view(), name='legacy_chat_get'),
    path('api/v1/ai/voice/', AiVoiceAssistantView.as_view(), name='ai_voice_direct'),

    # App Endpoints
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/plants/', include('plants.urls')),
    path('api/v1/disease/', include('disease.urls')),
    path('api/v1/ai/', include('ai_assistant.urls')),
    path('api/v1/tasks/', include('tasks.urls')),
    path('api/v1/community/', include('community.urls')),
    path('api/v1/marketplace/', include('marketplace.urls')),
    path('api/v1/expenses/', include('expenses.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
