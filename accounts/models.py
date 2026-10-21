from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        BUYER = "buyer", "Покупатель / Сатып алуучу"
        SUPPLIER = "supplier", "Поставщик / Жеткирүүчү"
        BOTH = "both", "Обе роли / Экөө тең"
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.BUYER)
    company_name = models.CharField(max_length=160, blank=True)
    city = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    about = models.TextField(blank=True)

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


    def __str__(self):
        return self.company_name or self.get_full_name() or self.username
