from django.urls import path
from .views import (
    AiChatView,
    AiChatHistoryView,
    AiConversationListView,
    AiVoiceAssistantView,
    AiConversationDeleteView
)

urlpatterns = [
    # AI Chat & Voice Messaging
    path('chat/', AiChatView.as_view(), name='ai_chat_send'),
    path('voice/', AiVoiceAssistantView.as_view(), name='ai_voice_assistant'),
    path('chat/history/<uuid:conversation_id>/', AiChatHistoryView.as_view(), name='ai_chat_history'),
    path('chat/conversations/', AiConversationListView.as_view(), name='ai_conversation_list'),
    path('chat/conversations/<uuid:conversation_id>/delete/', AiConversationDeleteView.as_view(), name='ai_conversation_delete'),
]
