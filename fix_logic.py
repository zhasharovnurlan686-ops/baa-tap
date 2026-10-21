from pathlib import Path
from datetime import datetime
import re

path = Path("marketplace/views.py")
source = path.read_text(encoding="utf-8")

backup = path.with_name(
    f"views.py.before_logic_fix_{datetime.now():%Y%m%d_%H%M%S}.bak"
)
backup.write_text(source, encoding="utf-8")

old_helper = '''def submission_rate_limited(request, action, limit=5, period=600):
    """РћРіСЂР°РЅРёС‡РёРІР°РµС‚ С‡Р°СЃС‚РѕС‚Сѓ POST-Р·Р°РїСЂРѕСЃРѕРІ РґР»СЏ Р°РІС‚РѕСЂРёР·РѕРІР°РЅРЅРѕРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
    if request.method != "POST" or request.user.is_staff:
        return False

    key = f"baatap:submit:{action}:{request.user.pk}"
    count = cache.get(key, 0)

    if count >= limit:
        return True

    cache.set(key, count + 1, timeout=period)
    return False
'''

new_helper = '''def submission_rate_limited(request, action, limit=5, period=600):
    """Check the submission limit without counting invalid form attempts."""
    if request.method != "POST" or request.user.is_staff:
        return False

    key = f"baatap:submit:{action}:{request.user.pk}"
    return cache.get(key, 0) >= limit


def record_submission(request, action, period=600):
    """Count a successfully saved submission."""
    if request.method != "POST" or request.user.is_staff:
        return

    key = f"baatap:submit:{action}:{request.user.pk}"
    if not cache.add(key, 1, timeout=period):
        cache.incr(key)
'''

if old_helper not in source:
    print("STOP: expected rate-limit function did not match.")
    print("No changes made. Backup:", backup)
    raise SystemExit(1)

source = source.replace(old_helper, new_helper, 1)

replacements = [
    (
        '        item.save()\n\n        messages.success(request, "Р—Р°РїСЂРѕСЃ',
        '        item.save()\n        record_submission(request, "request")\n\n        messages.success(request, "Р—Р°РїСЂРѕСЃ',
    ),
    (
        '        form.save()\n        messages.success(request, "Р—Р°РїСЂРѕСЃ РѕР±РЅРѕРІ',
        '        form.save()\n        record_submission(request, f"request-edit:{pk}")\n        messages.success(request, "Р—Р°РїСЂРѕСЃ РѕР±РЅРѕРІ',
    ),
    (
        '        offer.save()\n\n        messages.success(request, "РџСЂРµРґР»РѕР¶РµРЅРёРµ',
        '        offer.save()\n        record_submission(request, f"offer:{pk}")\n\n        messages.success(request, "РџСЂРµРґР»РѕР¶РµРЅРёРµ',
    ),
    (
        '        listing.save()\n        messages.success(request, "РџСЂРµРґР»РѕР¶РµРЅРёРµ',
        '        listing.save()\n        record_submission(request, "supplier-listing")\n        messages.success(request, "РџСЂРµРґР»РѕР¶РµРЅРёРµ',
    ),
]

for old, new in replacements:
    if old not in source:
        print("STOP: expected save block did not match:")
        print(old[:100])
        print("No changes written. Backup:", backup)
        raise SystemExit(1)
    source = source.replace(old, new, 1)

path.write_text(source, encoding="utf-8")
print("Updated:", path)
print("Backup:", backup)
