from django.urls import path
from .views import NotificationCenterView, MarkSingleNotificationReadView, MarkAllNotificationsReadView

urlpatterns = [
    path('', NotificationCenterView.as_view(), name='notification_list'),
    path('<int:pk>/read/', MarkSingleNotificationReadView.as_view(), name='mark_single_read'),
    path('read-all/', MarkAllNotificationsReadView.as_view(), name='mark_all_read'),
]
