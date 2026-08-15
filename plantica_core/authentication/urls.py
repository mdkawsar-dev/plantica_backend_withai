from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, UserViewSet, UserProfileViewSet,
    ForgotPasswordEmailView, OTPVerifyView, ResetPasswordView,
    UserProfileView, UserProfileUpdateView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile APIs
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='user_profile_update'),
    
    # Forget Password Flow Endpoints
    path('forgot-password/send-otp/', ForgotPasswordEmailView.as_view(), name='forgot_password_send_otp'),
    path('forgot-password/verify-otp/', OTPVerifyView.as_view(), name='forgot_password_verify_otp'),
    path('forgot-password/reset/', ResetPasswordView.as_view(), name='forgot_password_reset'),
    
    path('', include(router.urls)),
]
