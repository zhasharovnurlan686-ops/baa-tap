from pathlib import Path
from datetime import datetime
import re

path = Path("marketplace/views.py")
source = path.read_text(encoding="utf-8")

backup = path.with_name(
    f"views.py.before_text_repair_{datetime.now():%Y%m%d_%H%M%S}.bak"
)
backup.write_text(source, encoding="utf-8")

pattern = r"def role_required_for_catalog\(.*?(?=\ndef home\()"

replacement = '''def role_required_for_catalog(request, allowed_roles, redirect_name, role_label):
    """Проверяет доступ пользователя к разделу каталога."""
    if not request.user.is_authenticated:
        messages.info(
            request,
            "Войдите в аккаунт, чтобы просматривать этот раздел.",
        )
        return redirect("login")

    if request.user.is_staff or request.user.role in ("both", *allowed_roles):
        return None

    messages.error(
        request,
        f"Этот раздел доступен для следующих ролей: {role_label}. "
        "Изменить роль можно в профиле.",
    )
    return redirect(redirect_name)


def can_view_b2b_details(request):
    """Определяет, может ли пользователь видеть оптовые цены и объёмы."""
    if not request.user.is_authenticated:
        return False

    return (
        request.user.is_staff
        or request.user.verification_status == "verified"
    )

'''

updated, count = re.subn(pattern, replacement, source, count=1, flags=re.S)

if count != 1:
    print("ОШИБКА: нужный блок не найден. Исходный файл не изменён.")
    raise SystemExit(1)

updated = updated.replace(
    '"supplier_listing_list", "?????????"',
    '"supplier_listing_list", "покупателям и поставщикам"',
)

path.write_text(updated, encoding="utf-8")
print(f"Исправлен текст. Резервная копия: {backup}")
