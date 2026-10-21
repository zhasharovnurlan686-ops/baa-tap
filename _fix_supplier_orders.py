from pathlib import Path
import re
from datetime import datetime

root = Path(".")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
changed = []

def save_and_write(path, content):
    if path.read_text(encoding="utf-8-sig") == content:
        return
    backup = path.with_name(path.name + ".before_auto_fix_" + stamp)
    backup.write_bytes(path.read_bytes())
    path.write_text(content, encoding="utf-8")
    changed.append((str(path), str(backup)))
    print(f"ИСПРАВЛЕН: {path}")
    print(f"РЕЗЕРВНАЯ КОПИЯ: {backup}")

# 1. Восстанавливаем текст страницы списка заказов, который ранее оказался повреждён.
order_list = Path("templates/marketplace/order_list.html")
if order_list.exists():
    content = order_list.read_text(encoding="utf-8-sig")
    if "????" in content:
        content = '''{% extends "base.html" %}
{% block title %}Оптовые заказы — BaaTap KG{% endblock %}
{% block content %}
<section class="section">
  <div class="container">
    <h1>Оптовые заказы</h1>
    <div class="dashboard-panel">
      {% for order in orders %}
        <a class="dashboard-row" href="{% url 'order_detail' order.pk %}">
          <span class="dashboard-row-main">
            <b>Заказ №{{ order.pk }}</b>
            <small>
              {{ order.get_status_display }} · {{ order.created_at|date:"d.m.Y H:i" }}
              · Покупатель: {{ order.buyer.company_name|default:order.buyer.username }}
              · Поставщик: {{ order.supplier.company_name|default:order.supplier.username }}
            </small>
          </span>
        </a>
      {% empty %}
        <p>Оптовых заказов пока нет.</p>
        <a class="btn btn-primary" href="{% url 'supplier_listing_list' %}">Перейти в каталог поставщиков</a>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
'''
        save_and_write(order_list, content)

# 2. Ищем ссылку «Оптовые заказы», которая ошибочно ведёт в каталог поставщиков.
for path in Path("templates").rglob("*.html"):
    if ".before_" in path.name or ".backup" in path.name or ".bak" in path.name:
        continue
    try:
        content = path.read_text(encoding="utf-8-sig")
    except (UnicodeError, OSError):
        continue

    original = content
    pattern = re.compile(
        r'(<a\b[^>]*href=["\']\{% url [\'"]supplier_listing_list[\'"] %\}["\'][^>]*>)'
        r'(.*?)</a>',
        re.I | re.S
    )

    def fix_link(match):
        opening, label = match.groups()
        plain = re.sub(r"<[^>]+>", " ", label)
        low = plain.lower()
        # Меняем только пункт личного кабинета, явно относящийся к заказам.
        if ("оптов" in low and "заказ" in low) or (
            "????" in plain and "dashboard" in opening.lower()
        ):
            return opening.replace(
                "{% url 'supplier_listing_list' %}",
                "{% url 'order_list' %}"
            ).replace(
                '{% url "supplier_listing_list" %}',
                "{% url 'order_list' %}"
            ) + label + "</a>"
        return match.group(0)

    content = pattern.sub(fix_link, content)
    if content != original:
        save_and_write(path, content)

print("\n=== Проверка Django ===")
