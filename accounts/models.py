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

    def __str__(self):
        return self.company_name or self.get_full_name() or self.username
