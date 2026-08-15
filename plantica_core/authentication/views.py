import random
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import permissions, status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from plantica_core.responses import custom_response, success_response, error_response
from .models import UserProfile, PasswordResetOTP
from .serializers import (
    UserSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    RegisterSerializer, EmailLoginSerializer, ForgotPasswordEmailSerializer,
    OTPVerifySerializer, ResetPasswordSerializer
)
from plants.models import Plant
from tasks.models import GardeningTask
from expenses.models import GardeningExpense

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_user_profile_data(user):
    user_data = UserSerializer(user).data
    now = timezone.now()
    
    # Calculate screen 2 statistics
    total_plants = Plant.objects.filter(user=user).count()
    completed_tasks = GardeningTask.objects.filter(user=user, is_completed=True).count()
    current_month_expenses = GardeningExpense.objects.filter(
        user=user,
        date__year=now.year,
        date__month=now.month
    ).aggregate(total=Sum('amount'))['total'] or 0.0

    return {
        "user": user_data,
        "stats": {
            "total_plants": total_plants,
            "completed_tasks": completed_tasks,
            "current_month_expenses": float(current_month_expenses)
        }
    }


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            profile_data = get_user_profile_data(user)
            return success_response(
                data={
                    "profile": profile_data["user"],
                    "stats": profile_data["stats"],
                    "tokens": tokens
                },
                message="একাউন্ট সফলভাবে তৈরি হয়েছে",
                code=status.HTTP_201_CREATED
            )
        return error_response(
            message="একাউন্ট তৈরি ব্যর্থ হয়েছে",
            data=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            profile_data = get_user_profile_data(user)
            return success_response(
                data={
                    "profile": profile_data["user"],
                    "stats": profile_data["stats"],
                    "tokens": tokens
                },
                message="সফলভাবে লগইন হয়েছে",
                code=status.HTTP_200_OK
            )
        return error_response(
            message="লগইন ব্যর্থ হয়েছে",
            data=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return custom_response(
                    data=None,
                    message="Refresh token আবশ্যক।",
                    code=status.HTTP_400_BAD_REQUEST,
                    status=False
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return custom_response(
                data=None,
                message="সফলভাবে লগআউট করা হয়েছে।",
                code=status.HTTP_200_OK,
                status=True
            )
        except Exception as e:
            return custom_response(
                data=str(e),
                message="অকার্যকর বা মেয়াদোত্তীর্ণ টোকেন।",
                code=status.HTTP_400_BAD_REQUEST,
                status=False
            )


# --- 2nd Screen API: Get Profile API ---
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = get_user_profile_data(request.user)
        return success_response(
            data=data,
            message="প্রোফাইল তথ্য সফলভাবে পাওয়া গেছে",
            code=status.HTTP_200_OK
        )


# --- 1st Screen API: Edit/Update Profile API ---
class UserProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        return self.update_profile(request)

    def patch(self, request):
        return self.update_profile(request)

    def post(self, request):
        return self.update_profile(request)

    def update_profile(self, request):
        serializer = UserProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = get_user_profile_data(request.user)
            return success_response(
                data=data,
                message="প্রোফাইল সফলভাবে হালনাগাদ করা হয়েছে",
                code=status.HTTP_200_OK
            )
        return error_response(
            message="প্রোফাইল হালনাগাদ ব্যর্থ হয়েছে",
            data=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )


# --- Send OTP to Email View ---
class ForgotPasswordEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            
            otp_code = str(random.randint(1000, 9999))
            
            PasswordResetOTP.objects.filter(email=email).delete()
            PasswordResetOTP.objects.create(email=email, otp=otp_code)

            subject = "PLANTICA - পাসওয়ার্ড রিসেট OTP"
            message = f"আপনার পাসওয়ার্ড রিসেট করার জন্য ৪ ডিজিটের OTP কোডটি হলো: {otp_code}\n\nকোডটি ১০ মিনিটের জন্য কার্যকর থাকবে।"
            
            try:
                send_mail(subject, message, None, [email])
                return custom_response(
                    data={"email": email},
                    message="আপনার ইমেইলে ৪ ডিজিটের OTP কোড পাঠানো হয়েছে।",
                    status=True,
                    code=status.HTTP_200_OK
                )
            except Exception as e:
                return custom_response(
                    data=str(e),
                    message="ইমেইল পাঠাতে সমস্যা হয়েছে। পুনরায় চেষ্টা করুন।",
                    status=False,
                    code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return custom_response(
            data=serializer.errors,
            message="ভুল ইমেইল প্রদান করা হয়েছে",
            status=False,
            code=status.HTTP_400_BAD_REQUEST
        )


# --- OTP Verify View ---
class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            otp = serializer.validated_data['otp']

            otp_obj = PasswordResetOTP.objects.filter(email=email, otp=otp).last()

            if not otp_obj:
                return custom_response(
                    data=None,
                    message="ভুল OTP কোড দেওয়া হয়েছে।",
                    status=False,
                    code=status.HTTP_400_BAD_REQUEST
                )

            if not otp_obj.is_valid():
                return custom_response(
                    data=None,
                    message="OTP-এর মেয়াদ শেষ হয়ে গেছে। আবার চেষ্টা করুন।",
                    status=False,
                    code=status.HTTP_400_BAD_REQUEST
                )

            otp_obj.is_verified = True
            otp_obj.save()

            return custom_response(
                data={"email": email, "verified": True},
                message="OTP সফলভাবে যাচাই করা হয়েছে।",
                status=True,
                code=status.HTTP_200_OK
            )

        return custom_response(
            data=serializer.errors,
            message="যাচাইকরণ ব্যর্থ হয়েছে",
            status=False,
            code=status.HTTP_400_BAD_REQUEST
        )


# --- Reset Password View ---
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']

            otp_obj = PasswordResetOTP.objects.filter(email=email, otp=otp, is_verified=True).last()

            if not otp_obj or not otp_obj.is_valid():
                return custom_response(
                    data=None,
                    message="অনুমতি নেই। অনুগ্রহ করে প্রথমে OTP সঠিকভাবে যাচাই করুন।",
                    status=False,
                    code=status.HTTP_400_BAD_REQUEST
                )

            try:
                user = User.objects.get(email__iexact=email)
                user.set_password(new_password)
                user.save()

                otp_obj.delete()

                return custom_response(
                    data=None,
                    message="পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে। নতুন পাসওয়ার্ড দিয়ে লগইন করুন।",
                    status=True,
                    code=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return custom_response(
                    data=None,
                    message="ইউজার পাওয়া যায়নি।",
                    status=False,
                    code=status.HTTP_404_NOT_FOUND
                )

        return custom_response(
            data=serializer.errors,
            message="পাসওয়ার্ড রিসেট করা সম্ভব হয়নি",
            status=False,
            code=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Users fetched successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="User retrieved successfully")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, message="User updated successfully")
        return error_response(message="Update failed", data=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="User deleted successfully", code=status.HTTP_204_NO_CONTENT)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="User profiles fetched successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="User profile retrieved successfully")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, message="User profile updated successfully")
        return error_response(message="Profile update failed", data=serializer.errors)
