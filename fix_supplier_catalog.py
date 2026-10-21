from pathlib import Path
from datetime import datetime

path = Path("marketplace/views.py")
source = path.read_text(encoding="utf-8")

old = '''        .filter(
            is_active=True,
            supplier__role__in=["supplier", "both"],
        )
        .select_related("category", "supplier")
'''

new = '''        .filter(is_active=True)
        .select_related("category", "supplier")
        .order_by("-created_at")
'''

if old not in source:
    print("Ожидаемый участок кода не найден. Файл не изменён.")
    raise SystemExit(1)

backup = path.with_name(
    f"views.py_before_catalog_fix_{datetime.now():%Y%m%d_%H%M%S}.bak"
)
backup.write_text(source, encoding="utf-8")
source = source.replace(old, new, 1)
path.write_text(source, encoding="utf-8")

print("Исправлен каталог поставщиков.")
print("Резервная копия:", backup)
