from rest_framework import serializers
from .models import AiConversation, AiChatMessage


class AiChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiChatMessage
        fields = ['id', 'role', 'text', 'image', 'audio', 'created_at']
        read_only_fields = ['id', 'created_at']


class AiConversationSerializer(serializers.ModelSerializer):
    messages = AiChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = AiConversation
        fields = ['id', 'title', 'session_id', 'created_at', 'updated_at', 'message_count', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()
