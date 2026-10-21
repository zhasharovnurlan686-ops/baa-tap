from pathlib import Path
from datetime import datetime

path = Path("templates/marketplace/request_detail.html")
source = path.read_text(encoding="utf-8")

backup = path.with_name(
    f"request_detail_phone_fix_{datetime.now():%Y%m%d_%H%M%S}.bak"
)
backup.write_text(source, encoding="utf-8")

old = """href="https://wa.me/{{ item.buyer.phone|cut:' '|cut:'+'|cut:'('|cut:')'|cut:'-'|cut:'.' }}?text={{ 'Здравствуйте! Пишу по вашему запросу: '|add:item.title|urlencode }}%0A{{ request.build_absolute_uri|urlencode }}" """

new = """href="https://wa.me/{% with phone=item.buyer.phone|cut:' '|cut:'+'|cut:'('|cut:')'|cut:'-'|cut:'.' %}{% if phone|slice:':1' == '0' %}996{{ phone|slice:'1:' }}{% elif phone|slice:':3' == '996' %}{{ phone }}{% else %}{{ phone }}{% endif %}{% endwith %}?text={{ 'Здравствуйте! Пишу по вашему запросу: '|add:item.title|urlencode }}%0A{{ request.build_absolute_uri|urlencode }}" """

if old not in source:
    print("Не найдено исходное значение ссылки. Файл не изменён.")
    raise SystemExit(1)

source = source.replace(old, new, 1)
path.write_text(source, encoding="utf-8")

print("Номер телефона теперь преобразуется перед открытием WhatsApp.")
print("Резервная копия:", backup)
