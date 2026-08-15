from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
import datetime
from plantica_core.responses import custom_response
from .models import Notification
from .serializers import NotificationSerializer

# --- 1. Notification Center (New vs Older Grouped View) ---
class NotificationCenterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # Today's notifications
        new_notifications = Notification.objects.filter(
            user=user, 
            created_at__date=today
        ).order_by('-created_at')

        # Older notifications (before today)
        older_notifications = Notification.objects.filter(
            user=user, 
            created_at__date__lt=today
        ).order_by('-created_at')

        unread_count = Notification.objects.filter(user=user, is_read=False).count()

        new_serializer = NotificationSerializer(new_notifications, many=True)
        older_serializer = NotificationSerializer(older_notifications, many=True)

        data = {
            "unread_count": unread_count,
            "new_notifications": new_serializer.data,
            "older_notifications": older_serializer.data
        }

        return custom_response(
            data=data,
            message="বিজ্ঞপ্তিসমূহ সফলভাবে আনা হয়েছে",
            code=status.HTTP_200_OK,
            status=True
        )


# --- 2. Mark Single Notification Read View ---
class MarkSingleNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
            notif.is_read = True
            notif.save()
            return custom_response(
                data={"id": notif.id, "is_read": True},
                message="বিজ্ঞপ্তিটি পড়া হয়েছে হিসেবে চিহ্নিত করা হয়েছে",
                code=status.HTTP_200_OK,
                status=True
            )
        except Notification.DoesNotExist:
            return custom_response(
                data=None,
                message="বিজ্ঞপ্তি পাওয়া যায়নি",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )


# --- 3. Mark All Notifications Read View ---
class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return custom_response(
            data=None,
            message="সকল বিজ্ঞপ্তি পড়া হয়েছে হিসেবে চিহ্নিত করা হলো",
            code=status.HTTP_200_OK,
            status=True
        )
