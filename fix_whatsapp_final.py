from pathlib import Path
import re

p = Path("templates/marketplace/request_detail.html")
s = p.read_text(encoding="utf-8")
Path(str(p) + ".backup_whatsapp_final").write_text(s, encoding="utf-8")

# Удаляем старую вставку кнопки, если она уже есть
s = re.sub(
    r'\s*<a class="buyer-whatsapp-button".*?</a>',
    '',
    s,
    flags=re.S
)

# Находим карточку покупателя и вставляем кнопку сразу после неё
pattern = re.compile(
    r'(<div class="request-author">.*?</div>)\s*(\{% if user == item\.buyer %\}<a class="btn btn-secondary")',
    re.S
)

button = """
{% if user != item.buyer %}
<a class="buyer-whatsapp-button"
href="{% if item.buyer.phone %}https://wa.me/{% with phone=item.buyer.phone|cut:' '|cut:'+'|cut:'('|cut:')'|cut:'-'|cut:'.' %}{% if phone|slice:':1' == '0' %}996{{ phone|slice:'1:' }}{% else %}{{ phone }}{% endif %}{% endwith %}?text={{ 'Здравствуйте! Пишу по вашему запросу: '|add:item.title|urlencode }}{% else %}#{% endif %}"
{% if not item.buyer.phone %}onclick="alert('Покупатель не указал номер телефона в профиле.');return false;"{% endif %}
target="_blank" rel="noopener noreferrer"
style="display:inline-flex;align-items:center;justify-content:center;background:#25D366;color:#fff;padding:11px 18px;border-radius:9px;text-decoration:none;font-weight:700;margin:12px 8px 12px 0;">
Написать в WhatsApp
</a>
{% endif %}
"""

updated, count = pattern.subn(lambda m: m.group(1) + button + m.group(2), s, count=1)

if count != 1:
    print("Не удалось найти блок покупателя. Восстанавливаю исходный файл.")
    Path(str(p) + ".backup_whatsapp_final").replace(p)
    raise SystemExit(1)

p.write_text(updated, encoding="utf-8")
print("Кнопка WhatsApp вставлена после карточки покупателя.")
