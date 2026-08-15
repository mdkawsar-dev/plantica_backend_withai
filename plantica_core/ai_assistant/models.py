import uuid
from django.db import models
from django.conf import settings


class AiConversation(models.Model):
    """
    ব্যবহারকারী বা সেশনের এআই চ্যাট কনভারসেশন থ্রেড
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_conversations'
    )
    session_id = models.CharField(max_length=120, null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255, default="নতুন কৃষি পরামর্শ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.title} ({str(self.id)[:8]})"


class AiChatMessage(models.Model):
    """
    কনভারসেশনের প্রতিটি মেসেজ (টেক্সট, ছবি বা অডিও সহ)
    """
    ROLE_CHOICES = (
        ('user', 'User'),
        ('model', 'Model / Assistant'),
    )

    conversation = models.ForeignKey(
        AiConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    text = models.TextField(help_text="মেসেজ কন্টেন্ট")
    image = models.ImageField(upload_to='ai_chat/images/', null=True, blank=True)
    audio = models.FileField(upload_to='ai_chat/audio/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.text[:30]}..."
