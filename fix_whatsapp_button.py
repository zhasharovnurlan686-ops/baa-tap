from pathlib import Path
import re

p = Path("templates/marketplace/request_detail.html")
s = p.read_text(encoding="utf-8")
Path(str(p) + ".whatsapp-backup").write_text(s, encoding="utf-8")

if "buyer-whatsapp-button" not in s:
    marker = '<div class="sidebar-divider"></div>'

    button = """
{% if item.buyer.phone %}
<a class="buyer-whatsapp-button"
   href="https://wa.me/{% with phone=item.buyer.phone|cut:' '|cut:'+'|cut:'('|cut:')'|cut:'-'|cut:'.' %}{% if phone|slice:':1' == '0' %}996{{ phone|slice:'1:' }}{% else %}{{ phone }}{% endif %}{% endwith %}?text={{ 'Здравствуйте! Пишу по вашему запросу: '|add:item.title|urlencode }}"
   target="_blank" rel="noopener noreferrer"
   style="display:flex;align-items:center;justify-content:center;width:100%;box-sizing:border-box;background:#25D366;color:#fff;padding:14px 16px;border-radius:12px;text-decoration:none;font-weight:700;margin:16px 0;">
   Написать покупателю в WhatsApp
</a>
{% endif %}
"""
    if marker not in s:
        raise SystemExit("Не найден sidebar-divider. Файл сохранён без изменений.")
    s = s.replace(marker, button + marker, 1)
    p.write_text(s, encoding="utf-8")
    print("Кнопка добавлена в шаблон.")
else:
    print("Кнопка уже есть в шаблоне. Повторно не добавлял.")

print("Количество упоминаний кнопки:", s.count("buyer-whatsapp-button"))
