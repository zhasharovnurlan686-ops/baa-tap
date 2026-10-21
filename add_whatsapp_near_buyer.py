from pathlib import Path

p = Path("templates/marketplace/request_detail.html")
s = p.read_text(encoding="utf-8")
Path(str(p) + ".before_whatsapp_near_buyer").write_text(s, encoding="utf-8")

marker = """{% if user == item.buyer %}<a class="btn btn-secondary" href="{% url 'request_edit' item.pk %}">"""

button = """{% if user != item.buyer and item.buyer.phone %}
<a class="buyer-whatsapp-button"
href="https://wa.me/{% with phone=item.buyer.phone|cut:' '|cut:'+'|cut:'('|cut:')'|cut:'-'|cut:'.' %}{% if phone|slice:':1' == '0' %}996{{ phone|slice:'1:' }}{% else %}{{ phone }}{% endif %}{% endwith %}?text={{ 'Здравствуйте! Пишу по вашему запросу: '|add:item.title|urlencode }}"
target="_blank" rel="noopener noreferrer"
style="display:inline-flex;align-items:center;justify-content:center;background:#25D366;color:white;padding:10px 16px;border-radius:9px;text-decoration:none;font-weight:700;margin:10px 8px 10px 0;">
WhatsApp
</a>
"""

if "buyer-whatsapp-button" not in s:
    if marker not in s:
        print("Не найден блок рядом с кнопкой редактирования. Файл не изменён.")
        raise SystemExit(1)
    s = s.replace(marker, button + marker, 1)
    p.write_text(s, encoding="utf-8")
    print("Кнопка WhatsApp добавлена рядом с кнопкой редактирования.")
else:
    print("Кнопка WhatsApp уже есть в шаблоне.")
