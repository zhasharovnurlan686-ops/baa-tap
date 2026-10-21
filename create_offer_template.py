from pathlib import Path

Path("templates/marketplace/request_offers.html").write_text('''{% extends "base.html" %}
{% block title %}Коммерческие предложения — BaaTap KG{% endblock %}
{% block content %}
<section class="section">
  <div class="container">
    <a href="{% url 'request_detail' business_request.pk %}">← Вернуться к заявке</a>
    <h1>Коммерческие предложения</h1>
    <div class="dashboard-panel">
      <h2>{{ business_request.title }}</h2>
      <p>{{ business_request.description }}</p>
      {% for offer in offers %}
      <div class="dashboard-row">
        <span class="dashboard-row-main">
          <b>{{ offer.supplier.company_name|default:offer.supplier.username }}</b>
          <small>Срок: {{ offer.delivery_days }} дн. · {{ offer.get_status_display|default:offer.status }}</small>
          <small>{{ offer.details|default:"Дополнительные условия не указаны" }}</small>
        </span>
        <span class="row-end">{{ offer.price|floatformat:2 }} сом</span>
      </div>
      {% if offer.status == "pending" %}
      <form method="post" action="{% url 'accept_offer' offer.pk %}">
        {% csrf_token %}
        <button class="btn btn-primary" type="submit">Принять предложение и создать заказ</button>
      </form>
      {% endif %}
      {% empty %}
      <p>Коммерческих предложений пока нет.</p>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
''', encoding="utf-8")
print("Страница коммерческих предложений создана.")
