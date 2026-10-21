from pathlib import Path
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def save_backup(path):
    path = Path(path)
    if path.exists():
        backup = path.with_name(path.name + ".before_notifications_" + stamp)
        backup.write_bytes(path.read_bytes())
        print("Резервная копия:", backup.name)

# 1. Модель уведомлений
p = Path("marketplace/models.py")
src = p.read_text(encoding="utf-8")

if "class Notification(" not in src:
    save_backup(p)
    if "from django.conf import settings" not in src:
        src = "from django.conf import settings\n" + src
    src += '''

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="baatap_notifications",
        verbose_name="Получатель",
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="Заказ",
    )
    message = models.CharField(max_length=500, verbose_name="Сообщение")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return f"{self.recipient}: {self.message[:60]}"
'''
    p.write_text(src, encoding="utf-8")
    print("Модель Notification добавлена.")
else:
    print("Модель Notification уже существует.")

# 2. Сигналы: уведомлять участников при создании заказа и смене статуса
signals = Path("marketplace/signals.py")
signals.write_text('''from django.db.models.signals import pre_save, post_save
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
''', encoding="utf-8")
print("Сигналы уведомлений созданы.")

# 3. Регистрируем сигналы в приложении
apps_path = Path("marketplace/apps.py")
if not apps_path.exists():
    apps_path.write_text('''from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "marketplace"

    def ready(self):
        import marketplace.signals
''', encoding="utf-8")
    print("Создан marketplace/apps.py.")
else:
    app_src = apps_path.read_text(encoding="utf-8")
    if "import marketplace.signals" not in app_src:
        save_backup(apps_path)
        if "def ready(self):" in app_src:
            app_src = app_src.replace(
                "def ready(self):",
                "def ready(self):\n        import marketplace.signals",
                1,
            )
        else:
            app_src = app_src.rstrip() + '''

    def ready(self):
        import marketplace.signals
'''
        apps_path.write_text(app_src, encoding="utf-8")
        print("Сигналы зарегистрированы.")

# 4. Страница уведомлений
Path("marketplace/notification_views.py").write_text('''from django.contrib.auth.decorators import login_required
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
''', encoding="utf-8")
print("Страница уведомлений подключена.")

# 5. Маршруты
url_path = Path("marketplace/urls.py")
urls = url_path.read_text(encoding="utf-8")

if 'name="notification_list"' not in urls:
    save_backup(url_path)
    if "notification_views" not in urls:
        urls = urls.replace(
            "from . import views",
            "from . import notification_views, views",
            1,
        )
    urls = urls.replace(
        "urlpatterns = [",
        'urlpatterns = [\n'
        '    path("notifications/", notification_views.notification_list, name="notification_list"),\n'
        '    path("notifications/<int:pk>/read/", notification_views.notification_read, name="notification_read"),',
        1,
    )
    url_path.write_text(urls, encoding="utf-8")
    print("URL уведомлений добавлены.")

# 6. Шаблон уведомлений
template = Path("templates/marketplace/notifications.html")
template.parent.mkdir(parents=True, exist_ok=True)
template.write_text('''{% extends "base.html" %}
{% block title %}Уведомления — BaaTap KG{% endblock %}
{% block content %}
<section class="section">
  <div class="container">
    <h1>Уведомления</h1>
    <p>Непрочитанных: {{ unread_count }}</p>
    <div class="dashboard-panel">
      {% for notification in notifications %}
      <div class="dashboard-row">
        <div>
          <p><strong>{{ notification.message }}</strong></p>
          <small>{{ notification.created_at|date:"d.m.Y H:i" }}</small>
          {% if not notification.is_read %}
          <span> · Новое</span>
          {% endif %}
        </div>
        {% if notification.order_id %}
        <form method="post" action="{% url 'notification_read' notification.pk %}">
          {% csrf_token %}
          <button class="btn btn-primary" type="submit">Открыть заказ</button>
        </form>
        {% endif %}
      </div>
      {% empty %}
      <p>Пока уведомлений нет. Здесь появятся сообщения о заказах и изменении их статусов.</p>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
''', encoding="utf-8")
print("Шаблон уведомлений создан.")

# 7. Ссылка из панели управления, если шаблон существует
dashboard = Path("templates/dashboard/index.html")
if dashboard.exists():
    content = dashboard.read_text(encoding="utf-8")
    if "notification_list" not in content:
        save_backup(dashboard)
        link = '''
<a href="{% url 'notification_list' %}">Уведомления</a>
'''
        content = content.replace("{% endblock %}", link + "\n{% endblock %}", 1)
        dashboard.write_text(content, encoding="utf-8")
        print("Ссылка на уведомления добавлена в личный кабинет.")

print("Изменения внесены. Далее создаём миграцию.")
