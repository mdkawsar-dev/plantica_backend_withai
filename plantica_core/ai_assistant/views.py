import uuid
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from plantica_core.responses import custom_response, success_response, error_response
from .models import AiConversation, AiChatMessage
from .serializers import AiConversationSerializer, AiChatMessageSerializer
from .services import ask_plantica_ai_assistant


class AiChatView(APIView):
    """
    POST /api/v1/ai/chat/ অথবা /api/chat/send
    মাল্টিমোডাল এআই কৃষি চ্যাট ও ভয়েস অ্যাসিস্ট্যান্ট:
    - message: (text string) যেমন: "টমেটো গাছে কখন সার দেব?"
    - image: (optional file) গাছের পাতা, ফল বা বাগানের ছবি
    - audio: (optional file) বাংলা ভয়েস মেসেজ (.m4a, .mp3, .wav, .aac, .ogg)
    - conversation_id: (optional UUID) চলমান চ্যাট কন্টিনিউ করতে
    - session_id: (optional string) গেস্ট বা ডিভাইসের জন্য
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get('message', '').strip()
        conversation_id = request.data.get('conversation_id')
        session_id = request.data.get('session_id')
        image_file = request.FILES.get('image')
        audio_file = request.FILES.get('audio') or request.FILES.get('voice')

        if not user_message and not image_file and not audio_file:
            return error_response(
                message="অনুগ্রহ করে কোনো প্রশ্ন লিখুন, অথবা ছবি/ভয়েস রেকর্ড আপলোড করুন।",
                code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # ১. কনভারসেশন খুঁজে নেওয়া বা নতুন তৈরি করা
            conversation = None
            if conversation_id:
                try:
                    conversation = AiConversation.objects.get(id=conversation_id)
                except (AiConversation.DoesNotExist, ValueError):
                    pass

            if not conversation:
                title = user_message[:40] if user_message else ("ভয়েস বার্তা" if audio_file else "ছবি বিশ্লেষণ")
                user = request.user if request.user and request.user.is_authenticated else None
                conversation = AiConversation.objects.create(
                    user=user,
                    session_id=session_id or str(uuid.uuid4())[:8],
                    title=title
                )

            # ২. পূর্ববর্তী চ্যাট হিস্ট্রি সংগ্রহ
            past_messages = conversation.messages.all().order_by('created_at')[:10]
            chat_history = []
            for m in past_messages:
                chat_history.append({
                    "role": "user" if m.role == 'user' else "model",
                    "text": m.text
                })

            # ৩. ইউজারের মেসেজ ডাটাবেজে সেভ
            user_chat_msg = AiChatMessage.objects.create(
                conversation=conversation,
                role='user',
                text=user_message if user_message else ("🎙️ [ভয়েস বার্তা]" if audio_file else "📷 [ছবি বিশ্লেষণ]"),
                image=image_file,
                audio=audio_file
            )

            # ৪. জেমিনি এআই সার্ভিস কল করা
            ai_result = ask_plantica_ai_assistant(
                user_query=user_message,
                image_file=image_file,
                audio_file=audio_file,
                chat_history=chat_history
            )

            ai_answer = ai_result.get("answer", "")
            spoken_summary = ai_result.get("spoken_summary", "")
            suggested_followups = ai_result.get("suggested_followups", [])

            # ৫. এআই রেসপন্স ডাটাবেজে সেভ
            ai_chat_msg = AiChatMessage.objects.create(
                conversation=conversation,
                role='model',
                text=ai_answer
            )

            # আপডেট কনভারসেশন টাইটেল (যদি প্রথম মেসেজ হয়)
            if conversation.title == "নতুন কৃষি পরামর্শ" and user_message:
                conversation.title = user_message[:40]
                conversation.save()

            response_data = {
                "conversation_id": str(conversation.id),
                "user_message": AiChatMessageSerializer(user_chat_msg).data,
                "ai_message": AiChatMessageSerializer(ai_chat_msg).data,
                "spoken_summary": spoken_summary,
                "suggested_followups": suggested_followups,
                "used_model": ai_result.get("used_model", "gemini-3.5-flash")
            }

            return custom_response(
                data=response_data,
                message="এআই পরামর্শ সফলভাবে পাওয়া গেছে",
                code=status.HTTP_200_OK,
                status=True
            )

        except Exception as e:
            print(f"[AI Chat Error] {e}")
            return error_response(
                message=f"এআই উত্তর দিতে সমস্যা হয়েছে: {str(e)}",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AiChatHistoryView(APIView):
    """
    GET /api/v1/ai/chat/history/<conversation_id>/ অথবা /api/chat/get/<conversation_id>/
    একটি কনভারসেশনের সম্পূর্ণ চ্যাট হিস্ট্রি আনে।
    """
    permission_classes = [AllowAny]

    def get(self, request, conversation_id):
        try:
            conversation = AiConversation.objects.get(id=conversation_id)
            serializer = AiConversationSerializer(conversation)
            return success_response(
                data=serializer.data,
                message="চ্যাট হিস্ট্রি সফলভাবে পাওয়া গেছে"
            )
        except (AiConversation.DoesNotExist, ValueError):
            return error_response(
                message="কনভারসেশনটি পাওয়া যায়নি।",
                code=status.HTTP_404_NOT_FOUND
            )


class AiConversationListView(APIView):
    """
    GET /api/v1/ai/chat/conversations/ অথবা /api/chat/list/
    ইউজার বা ডিভাইসের পূর্ববর্তী সকল কনভারসেশনের তালিকা আনে।
    """
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.query_params.get('session_id')
        
        if request.user and request.user.is_authenticated:
            conversations = AiConversation.objects.filter(user=request.user)
        elif session_id:
            conversations = AiConversation.objects.filter(session_id=session_id)
        else:
            conversations = AiConversation.objects.none()

        serializer = AiConversationSerializer(conversations[:30], many=True)
        return success_response(
            data=serializer.data,
            message="কনভারসেশন তালিকা সফলভাবে পাওয়া গেছে"
        )


class AiVoiceAssistantView(APIView):
    """
    POST /api/v1/ai/voice/
    ডেডিকেটেড ভয়েস অ্যাসিস্ট্যান্ট এন্ডপয়েন্ট:
    - audio: (required voice file)
    - session_id / conversation_id: (optional)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        audio_file = request.FILES.get('audio') or request.FILES.get('voice')
        if not audio_file:
            return error_response(
                message="ভয়েস অডিও ফাইল আপলোড করা আবশ্যক।",
                code=status.HTTP_400_BAD_REQUEST
            )
        
        chat_view = AiChatView.as_view()
        return chat_view(request._request)


class AiConversationDeleteView(APIView):
    """
    DELETE /api/v1/ai/chat/conversations/<id>/delete/
    কনভারসেশন ডিলিট করার এন্ডপয়েন্ট।
    """
    permission_classes = [AllowAny]

    def delete(self, request, conversation_id):
        try:
            conversation = AiConversation.objects.get(id=conversation_id)
            conversation.delete()
            return success_response(
                message="কনভারসেশন সফলভাবে মুছে ফেলা হয়েছে",
                code=status.HTTP_204_NO_CONTENT
            )
        except (AiConversation.DoesNotExist, ValueError):
            return error_response(
                message="কনভারসেশনটি পাওয়া যায়নি।",
                code=status.HTTP_404_NOT_FOUND
            )
