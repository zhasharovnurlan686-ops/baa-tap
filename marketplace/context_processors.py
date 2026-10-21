from .models import Notification


def notification_context(request):
    count = 0
    user = getattr(request, "user", None)

    if user is not None and user.is_authenticated:
        count = Notification.objects.filter(
            recipient=user,
            is_read=False,
        ).count()

    return {"baatap_unread_notifications_count": count}
