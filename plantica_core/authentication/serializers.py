from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import UserProfile

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'avatar', 'gardening_type', 'address', 'latitude', 'longitude']


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name', read_only=True)
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'phone', 'role', 'profile']


class UserProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    def update(self, instance, validated_data):
        if 'name' in validated_data and validated_data['name']:
            instance.first_name = validated_data['name']

        if 'phone' in validated_data:
            instance.phone = validated_data['phone']

        instance.save()

        profile, _ = UserProfile.objects.get_or_create(user=instance)
        if 'address' in validated_data:
            profile.address = validated_data['address']

        if 'avatar' in validated_data and validated_data['avatar'] is not None:
            profile.avatar = validated_data['avatar']

        profile.save()
        return instance


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    confirm_password = serializers.CharField(write_only=True, min_length=6, required=True)
    gardening_type = serializers.ChoiceField(
        choices=['rooftop', 'balcony', 'agricultural_land', 'indoor'],
        required=True
    )

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("এই ইমেইলটি ইতিমধ্যে ব্যবহৃত হয়েছে।")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "পাসওয়ার্ড দু’টি মিলছে না।"})
        return attrs

    def create(self, validated_data):
        name = validated_data['name']
        email = validated_data['email']
        password = validated_data['password']
        gardening_type = validated_data['gardening_type']

        username = email.lower()
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name,
            role='farmer'
        )

        UserProfile.objects.update_or_create(
            user=user,
            defaults={'gardening_type': gardening_type}
        )

        return user


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user_obj = User.objects.get(email__iexact=email)
            username = user_obj.username
        except User.DoesNotExist:
            raise serializers.ValidationError("ইমেইল বা পাসওয়ার্ড ভুল হয়েছে।")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("ইমেইল বা পাসওয়ার্ড ভুল হয়েছে।")

        if not user.is_active:
            raise serializers.ValidationError("ব্যবহারকারীর অ্যাকাউন্টটি নিষ্ক্রিয় রয়েছে।")

        attrs['user'] = user
        return attrs


class ForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("এই ইমেইলটি দিয়ে কোনো অ্যাকাউন্ট পাওয়া যায়নি।")
        return value


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "পাসওয়ার্ড দুটি মিলছে না।"})
        return attrs
