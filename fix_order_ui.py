from pathlib import Path
from datetime import datetime
import re

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

files = [
    Path("templates/marketplace/order_detail.html"),
    Path("templates/marketplace/order_create.html"),
    Path("marketplace/forms.py"),
]

for path in files:
    backup = path.with_name(path.name + ".before_ui_fix_" + stamp)
    backup.write_bytes(path.read_bytes())
    print(f"Backup: {backup}")

detail = '''{% extends "base.html" %}
{% block title %}Заказ №{{ order.pk }} — BaaTap KG{% endblock %}
{% block content %}
<section class="section">
  <div class="container">
    <a href="{% url 'order_list' %}">← Все заказы</a>
    <h1>Заказ №{{ order.pk }}</h1>

    <div class="dashboard-panel">
      <p><strong>Статус:</strong> {{ order.get_status_display }}</p>
      <p><strong>Дата создания:</strong> {{ order.created_at|date:"d.m.Y H:i" }}</p>
      <p><strong>Покупатель:</strong> {{ order.buyer.company_name|default:order.buyer.username }}</p>
      <p><strong>Поставщик:</strong> {{ order.supplier.company_name|default:order.supplier.username }}</p>

      <h2>Состав заказа</h2>
      {% for item in order.items.all %}
        <div class="dashboard-row">
          <span class="dashboard-row-main">
            <b>{{ item.title }}</b>
            <small>{{ item.quantity }} шт. × {{ item.unit_price|floatformat:2 }} сом</small>
          </span>
          <span class="row-end">{{ item.line_total|floatformat:2 }} сом</span>
        </div>
      {% empty %}
        <p>В заказе пока нет товаров.</p>
      {% endfor %}

      <h2>Итого: {{ order.total_amount|floatformat:2 }} сом</h2>

      {% if order.buyer_note %}
        <p><strong>Комментарий покупателя:</strong> {{ order.buyer_note|linebreaksbr }}</p>
      {% endif %}

      {% if allowed_statuses %}
        <form method="post" action="{% url 'order_update_status' order.pk %}">
          {% csrf_token %}
          <label for="order-status">Изменить статус заказа</label>
          <select id="order-status" name="status" required>
            {% for value, label in allowed_statuses %}
              <option value="{{ value }}">{{ label }}</option>
            {% endfor %}
          </select>
          <button class="btn btn-primary" type="submit">Сохранить статус</button>
        </form>
      {% else %}
        <p>Изменение статуса сейчас недоступно.</p>
      {% endif %}
    </div>
  </div>
</section>
{% endblock %}
'''

create = '''{% extends "base.html" %}
{% block title %}Оформление заказа — BaaTap KG{% endblock %}
{% block content %}
<section class="section">
  <div class="container">
    <h1>Оформление оптового заказа</h1>
    <div class="dashboard-panel">
      <h2>{{ listing.title }}</h2>
      <p>Поставщик: {{ listing.supplier.company_name|default:listing.supplier.username }}</p>
      <p>Цена за единицу: <strong>{{ listing.price|floatformat:2 }} сом</strong></p>
      <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button class="btn btn-primary" type="submit">Подтвердить заказ</button>
        <a class="btn btn-secondary" href="{% url 'supplier_listing_detail' listing.pk %}">Назад к товару</a>
      </form>
      <p>После оформления заказ появится в разделе «Оптовые заказы».</p>
    </div>
  </div>
</section>
{% endblock %}
'''

Path("templates/marketplace/order_detail.html").write_text(detail, encoding="utf-8")
Path("templates/marketplace/order_create.html").write_text(create, encoding="utf-8")

forms_path = Path("marketplace/forms.py")
source = forms_path.read_text(encoding="utf-8")
start = source.find("class OrderCreateForm(forms.Form):")
if start == -1:
    raise SystemExit("Не найден OrderCreateForm. Файл форм не изменён.")

source = source[:start] + '''class OrderCreateForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=1000000,
        initial=1,
        label="Количество",
    )
    buyer_note = forms.CharField(
        required=False,
        max_length=2000,
        label="Комментарий к заказу",
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Укажите пожелания к заказу",
        }),
    )
'''
forms_path.write_text(source, encoding="utf-8")

print("Готово: страницы заказа и подписи формы восстановлены.")
