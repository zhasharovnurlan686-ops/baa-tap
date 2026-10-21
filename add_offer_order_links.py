from pathlib import Path
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def update_template(filename, marker, addition):
    path = Path(filename)
    if not path.exists():
        print(f"Файл не найден, пропускаю: {filename}")
        return

    content = path.read_text(encoding="utf-8")

    if marker in content:
        print(f"Ссылка уже добавлена: {filename}")
        return

    if "{% endblock %}" not in content:
        print(f"Не найден endblock: {filename}")
        return

    backup = path.with_name(path.name + ".before_offer_links_" + stamp)
    backup.write_bytes(path.read_bytes())

    content = content.replace(
        "{% endblock %}",
        addition + "\n{% endblock %}",
        1,
    )
    path.write_text(content, encoding="utf-8")
    print(f"Обновлено: {filename}; резервная копия: {backup.name}")

update_template(
    "templates/marketplace/request_detail.html",
    "request_offers",
    '''
<div class="dashboard-panel" style="margin-top:20px">
  <h3>Коммерческие предложения</h3>
  <p>Сравните цены, сроки поставки и условия поставщиков по этой заявке.</p>
  <a class="btn btn-primary"
     href="{% url 'request_offers' business_request.pk %}">
     Посмотреть предложения
  </a>
</div>
''',
)

update_template(
    "templates/marketplace/order_detail.html",
    "Исходная заявка",
    '''
{% if order.business_request %}
<section class="dashboard-panel" style="margin-top:20px">
  <h3>Исходная заявка</h3>
  <p>
    Заказ оформлен по заявке
    <strong>№{{ order.business_request.pk }}</strong>:
    {{ order.business_request.title }}
  </p>
  <a class="btn btn-primary"
     href="{% url 'request_detail' order.business_request.pk %}">
     Открыть заявку
  </a>
  {% if order.offer %}
  <p style="margin-top:12px">
    Коммерческое предложение №{{ order.offer.pk }} ·
    {{ order.offer.price|floatformat:2 }} сом
  </p>
  {% endif %}
</section>
{% endif %}
''',
)

print("Готово: ссылки на предложения и исходную заявку добавлены там, где найдены шаблоны.")
