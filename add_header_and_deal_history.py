from pathlib import Path
from datetime import datetime
import re

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def backup(path):
    path = Path(path)
    if path.exists():
        target = path.with_name(path.name + ".before_header_history_" + stamp)
        target.write_bytes(path.read_bytes())
        print("Backup:", target.name)

# 1. Контекст непрочитанных уведомлений
ctx = Path("marketplace/context_processors.py")
ctx.write_text('''from .models import Notification


def notification_context(request):
    count = 0
    user = getattr(request, "user", None)

    if user is not None and user.is_authenticated:
        count = Notification.objects.filter(
            recipient=user,
            is_read=False,
        ).count()

    return {"baatap_unread_notifications_count": count}
''', encoding="utf-8")
print("Контекст уведомлений создан.")

# 2. Подключаем контекстный процессор в настройках Django
settings_files = [
    Path("config/settings.py"),
    Path("baatap/settings.py"),
    Path("settings.py"),
]

settings_path = next((p for p in settings_files if p.exists()), None)

if settings_path:
    settings = settings_path.read_text(encoding="utf-8")
    processor = "marketplace.context_processors.notification_context"

    if processor not in settings:
        pattern = r'("context_processors"\s*:\s*\[)'
        if re.search(pattern, settings):
            backup(settings_path)
            settings = re.sub(
                pattern,
                r'\1\n                "marketplace.context_processors.notification_context",',
                settings,
                count=1,
            )
            settings_path.write_text(settings, encoding="utf-8")
            print("Контекстный процессор зарегистрирован:", settings_path)
        else:
            print("Не удалось найти TEMPLATES context_processors. Добавьте вручную:", processor)
    else:
        print("Контекстный процессор уже зарегистрирован.")
else:
    print("Не найден settings.py. Контекстный процессор создан, но требуется регистрация вручную.")

# 3. Находим общий шаблон сайта
base_candidates = [
    Path("templates/base.html"),
    Path("templates/base_base.html"),
    Path("marketplace/templates/base.html"),
]
base = next((p for p in base_candidates if p.exists()), None)

if base:
    html = base.read_text(encoding="utf-8")
    marker = "baatap-notifications-counter"

    if marker not in html:
        backup(base)
        snippet = '''
<a id="baatap-notifications-counter"
   href="{% url 'notification_list' %}"
   style="display:inline-flex;align-items:center;gap:7px;margin:6px 10px;text-decoration:none">
  Уведомления
  {% if bataap_unread_notifications_count %}
    <span style="display:inline-flex;align-items:center;justify-content:center;min-width:20px;height:20px;padding:0 5px;border-radius:20px;background:#dc3545;color:white;font-size:12px;font-weight:700">
      {{ bataap_unread_notifications_count }}
    </span>
  {% endif %}
</a>
'''
        if re.search(r"</nav\s*>", html, flags=re.I):
            html = re.sub(r"</nav\s*>", snippet + "\n</nav>", html, count=1, flags=re.I)
        elif re.search(r"</header\s*>", html, flags=re.I):
            html = re.sub(r"</header\s*>", snippet + "\n</header>", html, count=1, flags=re.I)
        else:
            html = html.replace("{% block content %}", snippet + "\n{% block content %}", 1)

        base.write_text(html, encoding="utf-8")
        print("Счётчик добавлен в:", base)
    else:
        print("Счётчик уже есть в:", base)
else:
    print("Общий шаблон base.html не найден. Счётчик создан не был.")

# 4. История сделки на странице заказа
detail = Path("templates/marketplace/order_detail.html")

if detail.exists():
    html = detail.read_text(encoding="utf-8")
    marker = "baatap-deal-history"

    if marker not in html:
        backup(detail)
        history = '''
<section id="baatap-deal-history" class="dashboard-panel" style="margin-top:24px">
  <h3>История сделки</h3>

  <div class="dashboard-row">
    <span>Заказ</span>
    <strong>№{{ order.pk }}</strong>
  </div>

  {% if order.business_request %}
  <div class="dashboard-row">
    <span>Исходная заявка</span>
    <span>
      №{{ order.business_request.pk }} — {{ order.business_request.title }}
      <a href="{% url 'request_detail' order.business_request.pk %}">Открыть заявку</a>
    </span>
  </div>

  <p>
    <a href="{% url 'request_offers' order.business_request.pk %}">
      Посмотреть предложения по заявке
    </a>
  </p>
  {% endif %}

  {% if order.offer %}
  <div class="dashboard-row">
    <span>Коммерческое предложение</span>
    <span>
      №{{ order.offer.pk }} · {{ order.offer.price|floatformat:2 }} сом
    </span>
  </div>
  <p>Статус предложения: {{ order.offer.get_status_display|default:order.offer.status }}</p>
  <p>Условия: {{ order.offer.details|default:"Не указаны" }}</p>
  {% else %}
  <p>Этот заказ оформлен не из коммерческого предложения.</p>
  {% endif %}

  <p>
    <a href="{% url 'notification_list' %}">Перейти к уведомлениям</a>
  </p>
</section>
'''
        if "{% endblock %}" in html:
            html = html.replace("{% endblock %}", history + "\n{% endblock %}", 1)
            detail.write_text(html, encoding="utf-8")
            print("История сделки добавлена в:", detail)
        else:
            print("Не найден endblock в order_detail.html.")
    else:
        print("История сделки уже добавлена.")
else:
    print("Не найден templates/marketplace/order_detail.html.")

print("Изменения сохранены.")
