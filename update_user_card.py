from pathlib import Path
import re

p = Path("templates/marketplace/request_detail.html")
s = p.read_text(encoding="utf-8")
Path(str(p) + ".before_user_card").write_text(s, encoding="utf-8")

pattern = re.compile(
    r'<div class="request-author">.*?</div>\s*\{% if user == item\.buyer %\}',
    re.S
)

replacement = """<div class="request-author">
<span class="fake-avatar">{{ item.buyer.company_name|default:item.buyer.get_full_name|default:item.buyer.username|slice:':1'|upper }}</span>
<span>
<b>{% if item.buyer.is_supplier %}Поставщик{% else %}Покупатель{% endif %}</b>
<strong>{{ item.buyer.company_name|default:item.buyer.get_full_name|default:item.buyer.username }}</strong>
<small>{{ item.buyer.city|default:"Бишкек" }}</small>
</span>
</div>
{% if user == item.buyer %}"""

updated, count = pattern.subn(replacement, s, count=1)

if count:
    p.write_text(updated, encoding="utf-8")
    print("Карточка пользователя обновлена.")
else:
    print("Не найден блок request-author. Файл не изменён.")
    raise SystemExit(1)
