from pathlib import Path

files = [
    Path("templates/base.html"),
    Path("templates/marketplace/home.html"),
    Path("templates/marketplace/request_list.html"),
    Path("templates/marketplace/request_form.html"),
    Path("templates/marketplace/request_detail.html"),
    Path("templates/accounts/register.html"),
    Path("templates/registration/login.html"),
]

markers = ("Рџ", "РЎ", "Рђ", "Рќ", "Р”", "СЂ", "СЃ", "вЂ", "Рѓ", "Р°")

for path in files:
    print(f"\n{'=' * 20} {path} {'=' * 20}")
    if not path.exists():
        print("Файл не найден")
        continue

    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except Exception as exc:
        print("Ошибка чтения:", exc)
        continue

    found = False
    for number, line in enumerate(lines, 1):
        if any(marker in line for marker in markers):
            print(f"{number}: {line[:350]}")
            found = True

    if not found:
        print("Подозрительных строк по выбранным маркерам не найдено.")
