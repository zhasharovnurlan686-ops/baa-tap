from django.conf import settings
from django.db import models
from django.urls import reverse

class Category(models.Model):
    name_ru = models.CharField(max_length=100)
    name_ky = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["name_ru"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    def __str__(self): return self.name_ru
    def localized_name(self, lang): return self.name_ky if lang == "ky" else self.name_ru

class BusinessRequest(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Открыта"
        PAUSED = "paused", "Приостановлена"
        CLOSED = "closed", "Закрыта"
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="business_requests")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="requests")
    title = models.CharField(max_length=180)
    description = models.TextField()
    quantity = models.CharField(max_length=120, blank=True, help_text="Например: 1000 штук")
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=80, blank=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Коммерческий запрос"
        verbose_name_plural = "Коммерческие запросы"
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse("request_detail", kwargs={"pk": self.pk})

class Offer(models.Model):
    request = models.ForeignKey(BusinessRequest, on_delete=models.CASCADE, related_name="offers")
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="offers")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_days = models.PositiveIntegerField(default=1)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["price", "created_at"]
        constraints = [models.UniqueConstraint(fields=["request", "supplier"], name="unique_offer_per_supplier_request")]
        verbose_name = "Предложение поставщика"
        verbose_name_plural = "Предложения поставщиков"
    def __str__(self): return f"{self.request.title} — {self.price} сом"
