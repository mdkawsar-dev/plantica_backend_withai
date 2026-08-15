from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    TYPE_CHOICES = (
        ('water', 'পানি দেওয়ার সময়'),
        ('fertilizer', 'সার দেওয়ার সময়'),
        ('pruning', 'ছাঁটাইয়ের সময়'),
        ('disease', 'রোগ সনাক্ত!'),
        ('community', 'নতুন কমিউনিটি পোস্ট'),
        ('tip', 'উদ্ভিদ পরিচর্যা টিপস'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} - {self.title}"
