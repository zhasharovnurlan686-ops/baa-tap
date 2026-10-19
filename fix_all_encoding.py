from pathlib import Path
from datetime import datetime
import re

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"

# Признаки текста, который ошибочно прочитали как Windows-1251.
BAD = ("Р°", "Р±", "РІ", "Рі", "Рґ", "Рµ", "Р¶", "Р·",
       "Рё", "Р№", "Рє", "Р»", "Рј", "РЅ", "Рѕ", "Рї",
       "Р°", "СЏ", "С‚", "СЃ", "СЂ", "С‹", "СЊ", "вЂ")

def damage_score(text):
    return sum(text.count(x) for x in BAD)

def repair_once(text):
    try:
        return text.encode("cp1251").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def repair(text):
    # Несколько проходов нужны, если строка была испорчена повторно.
    for _ in range(3):
        candidate = repair_once(text)
        if candidate == text or damage_score(candidate) >= damage_score(text):
            break
        text = candidate
    return text

if not TEMPLATES.exists():
    raise SystemExit(f"Папка шаблонов не найдена: {TEMPLATES}")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
changed_files = 0

for path in TEMPLATES.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in {".html", ".txt", ".js", ".css"}:
        continue

    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        print(f"ПРОПУСК: {path}")
        continue

    fixed = repair(original)

    if fixed != original:
        backup = path.with_name(path.name + f".{stamp}.bak")
        backup.write_text(original, encoding="utf-8")
        path.write_text(fixed, encoding="utf-8", newline="")
        changed_files += 1
        print(f"ИСПРАВЛЕН: {path.relative_to(ROOT)}")
        print(f"  Резервная копия: {backup.name}")

print(f"\nГотово. Изменено файлов: {changed_files}")
print("Проверь сайт перед публикацией.")
