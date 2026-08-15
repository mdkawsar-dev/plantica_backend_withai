from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('expert', 'Expert'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]

    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='farmer')

    def __str__(self):
        return f"{self.username} ({self.role})"


class UserProfile(models.Model):
    GARDENING_TYPE_CHOICES = [
        ('rooftop', 'Rooftop'),
        ('balcony', 'Balcony'),
        ('agricultural_land', 'Agricultural Land'),
        ('indoor', 'Indoor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    gardening_type = models.CharField(max_length=30, choices=GARDENING_TYPE_CHOICES, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_valid(self):
        # Valid for 10 minutes (600 seconds)
        time_difference = (timezone.now() - self.created_at).total_seconds()
        return time_difference <= 600

    def __str__(self):
        return f"OTP for {self.email}: {self.otp} (Verified: {self.is_verified})"
