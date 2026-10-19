from pathlib import Path

p = Path("templates/marketplace/home.html")
s = p.read_text(encoding="utf-8")

start = s.find('<div class="request-grid procurement-grid">')
if start == -1:
    start = s.find('<div class="request-grid')
if start == -1:
    raise SystemExit("Не найден контейнер карточек в home.html")

loop = s.find("{% for item in recent_requests %}", start)
if loop == -1:
    raise SystemExit("Не найден цикл карточек")

endfor = s.find("{% endfor %}", loop)
if endfor == -1:
    raise SystemExit("Не найден конец цикла")

end = s.find("</div>", endfor)
if end == -1:
    raise SystemExit("Не найден конец сетки карточек")
end += len("</div>")

new = r"""
<div class="request-grid procurement-grid">
  {% for item in recent_requests %}
    <article class="request-card procurement-card">
      <div class="request-meta">
        <span class="pill">{{ item.category.name_ru }}</span>
        <span>Опубликовано {{ item.created_at|date:'d.m.Y H:i' }}</span>
      </div>

      <h3><a href="{{ item.get_absolute_url }}">{{ item.title }}</a></h3>

      <div class="procurement-organization">
        <span class="procurement-label">Заказчик</span>
        <strong>{{ item.buyer.company_name|default:item.buyer.get_full_name|default:item.buyer.username }}</strong>
      </div>

      <div class="procurement-budget">
        <span class="procurement-label">Планируемый бюджет</span>
        <strong>
          {% if item.budget_min != None or item.budget_max != None %}
            {% if item.budget_min != None and item.budget_max != None %}
              {{ item.budget_min|floatformat:"-2" }} – {{ item.budget_max|floatformat:"-2" }} сом
            {% elif item.budget_min != None %}
              От {{ item.budget_min|floatformat:"-2" }} сом
            {% else %}
              До {{ item.budget_max|floatformat:"-2" }} сом
            {% endif %}
          {% else %}
            Цена по предложению поставщика
          {% endif %}
        </strong>
      </div>

      <p class="procurement-description">{{ item.description|truncatechars:160 }}</p>

      {% if item.quantity %}
        <div class="procurement-quantity">
          <span class="procurement-label">Количество / объём</span>
          <span>{{ item.quantity }}</span>
        </div>
      {% endif %}

      <div class="procurement-dates">
        <div>
          <span class="procurement-label">Дата публикации</span>
          <strong>{{ item.created_at|date:'d.m.Y' }}</strong>
        </div>
        <div>
          <span class="procurement-label">Срок подачи предложений</span>
          <strong>{% if item.deadline %}{{ item.deadline|date:'d.m.Y' }}{% else %}Не указан{% endif %}</strong>
        </div>
      </div>

      <div class="procurement-bottom">
        <span>⌖ {{ item.city|default:'Кыргызстан' }}</span>
        <span>Предложений: {{ item.offers.count }}</span>
      </div>

      <a class="btn btn-primary btn-block procurement-action" href="{{ item.get_absolute_url }}">Посмотреть заявку и условия →</a>
    </article>
  {% empty %}
    <div class="empty-state">
      Пока нет опубликованных запросов.
      <a href="{% url 'request_create' %}">Создайте первый запрос</a>.
    </div>
  {% endfor %}
</div>
"""

backup = p.with_name("home.html.encoding-backup")
if not backup.exists():
    backup.write_text(s, encoding="utf-8")

p.write_text(s[:start] + new + s[end:], encoding="utf-8")

check = p.read_text(encoding="utf-8")
print("Шаблон обновлён:", p.resolve())
print("Русский текст записан:", "Планируемый бюджет" in check)
print("Есть вопросительные знаки вместо текста:", "????????" in check)
