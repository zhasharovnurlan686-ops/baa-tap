from pathlib import Path
from datetime import datetime
import re

path = Path("marketplace/order_views.py")
source = path.read_text(encoding="utf-8")

pattern = re.compile(r'f?"[^"\n]*\?{3,}[^"\n]*"')
matches = list(pattern.finditer(source))

print("Повреждённых строковых литералов:", len(matches))
for match in matches:
    print(" ", match.group())

expected = [
    ("Оформлять заказ могут только покупатели ",
     "с подтверждённой компанией."),
    ("Нельзя оформлять заказ на собственное предложение.",),
    ("У предложения должна быть указана положительная цена.",),
    ("Нельзя оформлять заказ на собственное предложение.",),
    ("У предложения не указана цена для оформления заказа.",),
    ("Заказ №{order.pk} создан.",),
    ("Недопустимый переход статуса заказа.",),
    ("Статус заказа обновлён.",),
]

if len(matches) != sum(len(group) for group in expected):
    raise SystemExit(
        "Количество строк отличается от ожидаемого. "
        "Файл не изменён — проверь вывод выше."
    )

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = path.with_name(path.name + ".before_messages_" + stamp)
backup.write_bytes(path.read_bytes())

index = 0
def replace_literal(match):
    global index
    group_index = 0
    offset = 0
    for group in expected:
        if offset <= index < offset + len(group):
            replacement = group[index - offset]
            break
        offset += len(group)
    index += 1
    if "{order.pk}" in replacement:
        return 'f"' + replacement + '"'
    return '"' + replacement + '"'

updated = pattern.sub(replace_literal, source)

if re.search(r'\?{3,}', updated):
    raise SystemExit("Остались повреждённые строки. Проверь файл.")

path.write_text(updated, encoding="utf-8")
print("Резервная копия:", backup)
print("Сообщения восстановлены.")
