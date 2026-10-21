from pathlib import Path
from datetime import datetime

path = Path("templates/marketplace/home.html")
source = path.read_text(encoding="utf-8")

start_marker = '<section class="section" id="home-supplier-listings">'
end_marker = '{% endblock %}'

start = source.find(start_marker)
end = source.find(end_marker, start)

if start == -1 or end == -1:
    print("Не удалось определить границы блока. Файл не изменён.")
    raise SystemExit(1)

old_block = source[start:end]

if "supplier-card" in old_block:
    print("Похоже, карточки уже обновлены. Повторное изменение не требуется.")
    raise SystemExit(0)

backup = path.with_name(
    f"home.html_before_supplier_design_{datetime.now():%Y%m%d_%H%M%S}.bak"
)
backup.write_text(source, encoding="utf-8")

new_block = '''<section class="section supplier-catalog-section" id="home-supplier-listings">
  <div class="container">
    <div class="section-heading supplier-results-heading">
      <div>
        <div class="eyebrow">BaaTap KG / Каталог поставщиков</div>
        <h2>Товары и услуги для вашего бизнеса</h2>
        <p>Изучайте предложения, сравнивайте цены и выбирайте партнёров.</p>
      </div>
      <a class="text-link" href="{% url 'supplier_listing_list' %}">
        Все предложения <span>→</span>
      </a>
    </div>

    <div class="request-grid supplier-grid">
      {% for item in supplier_listings %}
        <article class="request-card supplier-card">
          <a class="supplier-card-image" href="{{ item.get_absolute_url }}" aria-label="{{ item.title }}">
            {% if item.image_url %}
              <img src="{{ item.image_url }}" alt="{{ item.title }}" loading="lazy">
            {% else %}
              <div class="supplier-image-placeholder">
                <span>BAATAP KG</span>
                <strong>{{ item.category.name_ru }}</strong>
              </div>
            {% endif %}
          </a>

          <div class="supplier-card-body">
            <div class="supplier-card-meta">
              <span class="pill">{{ item.category.name_ru }}</span>
              <span class="supplier-date">{{ item.created_at|date:"d.m.Y" }}</span>
            </div>

            <h3 class="supplier-card-title">
              <a href="{{ item.get_absolute_url }}">{{ item.title }}</a>
            </h3>

            <p class="supplier-card-description">{{ item.description|truncatechars:150 }}</p>

            <div class="supplier-company">
              <span class="supplier-company-icon">B2B</span>
              <div>
                <span class="supplier-muted-label">Поставщик</span>
                <strong>{{ item.supplier.company_name|default:item.supplier.get_full_name|default:item.supplier.username }}</strong>
              </div>
            </div>

            <div class="supplier-price-panel">
              <span>Стоимость</span>
              <strong>
                {% if item.price != None %}
                  {{ item.price|floatformat:"-2" }} <small>сом</small>
                {% else %}
                  По договорённости
                {% endif %}
              </strong>
            </div>

            <div class="supplier-facts">
              {% if item.quantity %}
                <div class="supplier-fact">
                  <span class="supplier-fact-symbol">▦</span>
                  <div><span>Количество</span><strong>{{ item.quantity }}</strong></div>
                </div>
              {% endif %}
              <div class="supplier-fact">
                <span class="supplier-fact-symbol">⌖</span>
                <div><span>Город</span><strong>{{ item.city|default:"Кыргызстан" }}</strong></div>
              </div>
            </div>

            <a class="btn btn-primary btn-block supplier-details-button" href="{{ item.get_absolute_url }}">
              Подробнее о предложении <span>→</span>
            </a>
          </div>
        </article>
      {% empty %}
        <div class="empty-state supplier-empty">
          <h3>Пока нет предложений поставщиков</h3>
          <p>Здесь появятся товары и услуги компаний, зарегистрированных на BaaTap KG.</p>
          <a class="btn btn-secondary" href="{% url 'supplier_listing_list' %}">Открыть каталог</a>
        </div>
      {% endfor %}
    </div>

    <div class="supplier-home-footer">
      <a class="btn btn-secondary" href="{% url 'supplier_listing_list' %}">
        Перейти в каталог поставщиков →
      </a>
      {% if user.is_authenticated %}
        {% if user.role == "supplier" or user.role == "both" or user.is_staff %}
          <a class="btn btn-primary" href="{% url 'supplier_listing_create' %}">
            + Разместить предложение
          </a>
        {% endif %}
      {% else %}
        <a class="btn btn-primary" href="{% url 'login' %}?next={% url 'supplier_listing_create' %}">
          Стать поставщиком
        </a>
      {% endif %}
    </div>
  </div>
</section>

'''

source = source[:start] + new_block + source[end:]
path.write_text(source, encoding="utf-8")

print("Главная страница обновлена.")
print("Резервная копия:", backup)
