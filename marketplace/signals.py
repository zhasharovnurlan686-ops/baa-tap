from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Order, Notification


@receiver(pre_save, sender=Order)
def remember_order_status(sender, instance, **kwargs):
    if instance.pk:
        instance._old_status = (
            sender.objects.filter(pk=instance.pk)
            .values_list("status", flat=True)
            .first()
        )
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def notify_order_participants(sender, instance, created, **kwargs):
    old_status = getattr(instance, "_old_status", None)

    if created:
        message = f"Создан заказ №{instance.pk}. Проверьте подробности заказа."
    elif old_status != instance.status:
        try:
            status_label = instance.get_status_display()
        except (AttributeError, TypeError):
            status_label = str(instance.status)
        message = f"Статус заказа №{instance.pk} изменён: {status_label}."
    else:
        return

    recipient_ids = set()
    for field in ("buyer", "supplier"):
        user = getattr(instance, field, None)
        if user is not None:
            recipient_ids.add(user.pk)

    for user_id in recipient_ids:
        Notification.objects.create(
            recipient_id=user_id,
            order=instance,
            message=message,
        )
