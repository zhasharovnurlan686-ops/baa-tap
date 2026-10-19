from pathlib import Path
from datetime import datetime
import re

path = Path("templates/marketplace/home.html")
original = path.read_text(encoding="utf-8")

backup = path.with_name(
    path.name + "." + datetime.now().strftime("%Y%m%d_%H%M%S") + ".bak"
)
backup.write_text(original, encoding="utf-8")

markers = re.compile(r"Р[А-Яа-яЁё]|С[А-Яа-яЁё]|вЂ")

def repair_token(match):
    token = match.group(0)

    if not markers.search(token):
        return token

    try:
        candidate = token.encode("cp1251").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return token

    # Заменяем слово, только если подозрительных маркеров стало меньше.
    if len(markers.findall(candidate)) < len(markers.findall(token)):
        return candidate

    return token

fixed = re.sub(r"\S+", repair_token, original)

if fixed == original:
    print("Автоматическое исправление ничего не изменило.")
    print("Резервная копия:", backup)
else:
    path.write_text(fixed, encoding="utf-8")
    print("Главная страница исправлена:", path)
    print("Резервная копия:", backup)
    print("Проверь текст в браузере: http://127.0.0.1:8000/")
