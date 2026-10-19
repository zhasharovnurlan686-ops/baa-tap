from pathlib import Path
from datetime import datetime
import re
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / f"encoding_backup_{STAMP}"
EXTENSIONS = {".html", ".py", ".css", ".js", ".txt", ".json", ".xml", ".svg"}
SKIP_DIRS = {
    ".venv", ".git", "__pycache__", "node_modules",
    "staticfiles", "media", "encoding_backup"
}
MARKERS = re.compile(r"Р[А-Яа-яЁё]|С[А-Яа-яЁё]|вЂ|Ð|Ñ")

def score(text):
    return len(MARKERS.findall(text))

def repair_text(text):
    changed = False

    # Несколько проходов исправляют также двойное искажение кодировки.
    for _ in range(3):
        parts = re.split(r"(\s+)", text)
        new_parts = []

        for part in parts:
            if not part or part.isspace() or score(part) == 0:
                new_parts.append(part)
                continue

            candidate = part
            try:
                for encoding in ("cp1251", "latin1"):
                    try:
                        decoded = candidate.encode(encoding).decode("utf-8")
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        continue

                    if score(decoded) < score(candidate):
                        candidate = decoded
                        break
            except Exception:
                pass

            if candidate != part:
                changed = True
            new_parts.append(candidate)

        updated = "".join(new_parts)
        if updated == text:
            break
        text = updated

    return text, changed

# Резервные копии всех файлов, которые будут изменены.
file_changes = []

for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
        continue
    relative = path.relative_to(ROOT)

    if any(part in SKIP_DIRS for part in relative.parts):
        continue
    if "migrations" in relative.parts:
        continue
    if relative.parts[0].startswith("encoding_backup_"):
        continue
    if path.name.startswith(("fix_", "repair_", "diagnose_", "check_encoding")):
        continue

    try:
        original = path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError):
        continue

    fixed, changed = repair_text(original)
    if changed and fixed != original:
        file_changes.append((path, original, fixed))

if file_changes:
    for path, original, fixed in file_changes:
        backup_path = BACKUP / path.relative_to(ROOT)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        path.write_text(fixed, encoding="utf-8")

print(f"Изменено файлов проекта: {len(file_changes)}")
if file_changes:
    print(f"Резервные копии: {BACKUP}")

# Исправление текстовых полей Django в базе данных.
try:
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django
    django.setup()

    from django.apps import apps
    from django.db import transaction

    db_changes = 0

    with transaction.atomic():
        for model in apps.get_models():
            fields = [
                field for field in model._meta.concrete_fields
                if field.get_internal_type() in ("CharField", "TextField")
                and not field.primary_key
            ]
            if not fields:
                continue

            for obj in model.objects.all().iterator():
                updates = {}

                for field in fields:
                    value = getattr(obj, field.name, None)
                    if not isinstance(value, str):
                        continue

                    fixed, changed = repair_text(value)
                    if changed and fixed != value:
                        updates[field.name] = fixed

                if updates:
                    for name, value in updates.items():
                        setattr(obj, name, value)
                    obj.save(update_fields=list(updates))
                    db_changes += len(updates)

    print(f"Исправлено текстовых полей базы данных: {db_changes}")

except Exception as exc:
    print("База данных не исправлена автоматически.")
    print(f"Причина: {type(exc).__name__}: {exc}")
    print("Файлы проекта обработаны независимо от базы данных.")

print("Готово.")
