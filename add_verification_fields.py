from pathlib import Path

# 1. Поля компании и статуса проверки
model_path = Path("accounts/models.py")
model_text = model_path.read_text(encoding="utf-8")
marker = "    about = models.TextField(blank=True)"

addition = '''
    company_registration_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Регистрационный номер компании",
    )
    class VerificationStatus(models.TextChoices):
        UNVERIFIED = "unverified", "Не проверена"
        PENDING = "pending", "На проверке"
        VERIFIED = "verified", "Подтверждена"
        REJECTED = "rejected", "Отклонена"

    verification_status = models.CharField(
        max_length=12,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
        verbose_name="Статус проверки компании",
    )
'''

if "verification_status = models.CharField(" not in model_text:
    if marker not in model_text:
        raise SystemExit("ОСТАНОВКА: не найдено поле about в accounts/models.py")
    model_text = model_text.replace(marker, marker + "\n" + addition, 1)
    model_path.write_text(model_text, encoding="utf-8")
    print("Добавлены поля в accounts/models.py")
else:
    print("Поля проверки уже существуют — модель не изменена")

# 2. Добавляем регистрационный номер в форму профиля
forms_path = Path("accounts/forms.py")
forms_text = forms_path.read_text(encoding="utf-8")

profile_marker = '''            "company_name", "city", "phone", "about",
'''
profile_replacement = '''            "company_name", "company_registration_number",
            "city", "phone", "about",
'''

if '"company_registration_number"' not in forms_text:
    if profile_marker not in forms_text:
        raise SystemExit("ОСТАНОВКА: не найден список полей ProfileForm")
    forms_text = forms_text.replace(profile_marker, profile_replacement, 1)

label_marker = '''            "company_name":'''
if '"company_registration_number":' not in forms_text:
    position = forms_text.find(label_marker, forms_text.find("class ProfileForm"))
    if position == -1:
        raise SystemExit("ОСТАНОВКА: не найден блок labels ProfileForm")
    forms_text = forms_text[:position] + '''            "company_registration_number": "Регистрационный номер компании",
''' + forms_text[position:]

forms_path.write_text(forms_text, encoding="utf-8")
print("Обновлена форма профиля")
