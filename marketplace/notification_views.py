from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related("order")
    return render(request, "marketplace/notifications.html", {
        "notifications": notifications,
        "unread_count": notifications.filter(is_read=False).count(),
    })


@login_required
@require_POST
def notification_read(request, pk):
    notification = get_object_or_404(
        Notification, pk=pk, recipient=request.user
    )
    notification.is_read = True
    notification.save(update_fields=["is_read"])

    if notification.order_id:
        return redirect("order_detail", pk=notification.order_id)
    return redirect("notification_list")
