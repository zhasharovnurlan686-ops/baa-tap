from pathlib import Path
from datetime import datetime
import shutil

base = Path("templates/base.html")
home = Path("templates/marketplace/home.html")

for p in (base, home):
    if not p.exists():
        raise SystemExit(f"Не найден файл: {p}")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = Path(f"backup_roles_{stamp}")
(backup / "templates/marketplace").mkdir(parents=True)

shutil.copy2(base, backup / "templates/base.html")
shutil.copy2(home, backup / "templates/marketplace/home.html")

# --- Меню в base.html ---
text = base.read_text(encoding="utf-8-sig")

start_marker = '            <a href="{% url \'supplier_listing_list\' %}">'
if start_marker in text:
    start = text.index(start_marker)
    end = text.index("</nav>", start)
    supplier_link = text[start:end]
    supplier_link = supplier_link.replace(
        '            <a href="{% url \'supplier_listing_list\' %}">',
        '            {% if user.role == "supplier" or user.role == "both" or user.is_staff %}\n'
        '            <a href="{% url \'supplier_listing_list\' %}">'
    )
    supplier_link = supplier_link.rstrip() + "\n            {% endif %}\n"
    text = text[:start] + supplier_link + text[end:]

# Исправляем блок меню между header/nav осторожно:
# добавляем доступные покупателю ссылки, не меняя существующие URL.
if 'url \'request_list\'' not in text:
    anchor = '                <a href="{% url \'dashboard\' %}">'
    if anchor in text:
        pos = text.index(anchor)
        text = text[:pos] + (
            '                {% if user.role == "buyer" or user.role == "both" or user.is_staff %}\n'
            '                <a href="{% url \'request_list\' %}">Заявки покупателей</a>\n'
            '                <a href="{% url \'request_create\' %}">Создать заявку</a>\n'
            '                {% endif %}\n'
        ) + text[pos:]

base.write_text(text, encoding="utf-8")

# --- Кнопки на главной странице ---
text = home.read_text(encoding="utf-8-sig")

old_actions = '''      <div class="hero-actions">
        <a class="btn btn-primary" href="{% url 'request_create' %}">
          {% if request.LANGUAGE_CODE == 'ky' %}РЎСѓСЂРѕРѕ-С‚Р°Р»Р°Рї С‚ТЇР·ТЇТЇ{% else %}РЎРѕР·РґР°С‚СЊ Р·Р°РїСЂРѕСЃ{% endif %}
          <span>в†’</span>
        </a>
        <a class="btn btn-secondary" href="{% url 'request_list' %}">
          {% if request.LANGUAGE_CODE == 'ky' %}РЎСѓСЂРѕРѕ-С‚Р°Р»Р°РїС‚Р°СЂРґС‹ РєУ©СЂТЇТЇ{% else %}РЎРјРѕС‚СЂРµС‚СЊ Р·Р°РїСЂРѕСЃС‹{% endif %}
        </a>
      </div>'''

if old_actions in text:
    new_actions = '''      <div class="hero-actions">
        {% if user.is_authenticated %}
          {% if user.role == "buyer" or user.role == "both" or user.is_staff %}
            <a class="btn btn-primary" href="{% url 'request_create' %}">
              Создать заявку <span>→</span>
            </a>
            <a class="btn btn-secondary" href="{% url 'request_list' %}">
              Смотреть заявки
            </a>
          {% endif %}
          {% if user.role == "supplier" or user.role == "both" or user.is_staff %}
            <a class="btn btn-primary" href="{% url 'supplier_listing_list' %}">
              Каталог предложений
            </a>
            <a class="btn btn-secondary" href="{% url 'supplier_listing_create' %}">
              Разместить предложение
            </a>
          {% endif %}
        {% else %}
          <a class="btn btn-primary" href="{% url 'register' %}">
            Зарегистрироваться <span>→</span>
          </a>
          <a class="btn btn-secondary" href="{% url 'request_list' %}">
            Смотреть заявки
          </a>
        {% endif %}
      </div>'''
    text = text.replace(old_actions, new_actions, 1)
else:
    print("Внимание: блок кнопок главной страницы не совпал с ожидаемым текстом; главная не изменена.")

home.write_text(text, encoding="utf-8")

print("Готово. Резервные копии:", backup.resolve())
