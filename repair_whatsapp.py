from pathlib import Path

p = Path("templates/marketplace/request_detail.html")
s = p.read_text(encoding="utf-8")

backup = Path(str(p) + ".before_whatsapp_repair")
if not backup.exists():
    backup.write_text(s, encoding="utf-8")

# Убираем только ранее добавленные WhatsApp-кнопки
start = '<a class="buyer-whatsapp-button"'
while start in s:
    i = s.find(start)
    j = s.find("</a>", i)
    if j == -1:
        break
    s = s[:i] + s[j + 4:]

marker = """{% if user == item.buyer %}<a class="btn btn-secondary" href="{% url 'request_edit' item.pk %}">"""

button = """{% if user != item.buyer %}
{% if item.buyer.phone %}
<a class="buyer-whatsapp-button" href="https://wa.me/{% with phone=item.buyer.phone|cut:' '|cut:'+'|cut:'('|cut:')'|cut:'-'|cut:'.' %}{% if phone|slice:':1' == '0' %}996{{ phone|slice:'1:' }}{% else %}{{ phone }}{% endif %}{% endwith %}?text={{ 'Здравствуйте! Пишу по вашему запросу: '|add:item.title|urlencode }}" target="_blank" rel="noopener noreferrer" style="display:inline-flex;background:#25D366;color:white;padding:12px 18px;border-radius:9px;text-decoration:none;font-weight:bold;margin:12px 8px 12px 0;">Написать в WhatsApp</a>
{% else %}
<a class="buyer-whatsapp-button" href="#" onclick="alert('Покупатель не указал номер телефона в профиле.');return false;" style="display:inline-flex;background:#25D366;color:white;padding:12px 18px;border-radius:9px;text-decoration:none;font-weight:bold;margin:12px 8px 12px 0;">Написать в WhatsApp</a>
{% endif %}
{% endif %}
"""

if "buyer-whatsapp-button" in s:
    print("Не удалось удалить старую кнопку полностью. Остановлено.")
    raise SystemExit(1)

if marker not in s:
    print("Не найдено место вставки кнопки. Файл не изменён.")
    print("Выполни: Select-String -Path .\\templates\\marketplace\\request_detail.html -Pattern 'request_edit|request-author'")
    raise SystemExit(1)

s = s.replace(marker, button + marker, 1)
p.write_text(s, encoding="utf-8")

print("Кнопка вставлена в шаблон:", p)
print("Проверка:", s.count("buyer-whatsapp-button"), "кнопка(и)")
