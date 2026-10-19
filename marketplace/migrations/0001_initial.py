from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name_ru", models.CharField(max_length=100)),
                ("name_ky", models.CharField(max_length=100)),
                ("slug", models.SlugField(unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name_ru"], "verbose_name": "Категория", "verbose_name_plural": "Категории"},
        ),
        migrations.CreateModel(
            name="BusinessRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("description", models.TextField()),
                ("quantity", models.CharField(blank=True, help_text="Например: 1000 штук", max_length=120)),
                ("budget_min", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("budget_max", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("city", models.CharField(blank=True, max_length=80)),
                ("deadline", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("open", "Открыта"), ("paused", "Приостановлена"), ("closed", "Закрыта")], default="open", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("buyer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="business_requests", to=settings.AUTH_USER_MODEL)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="requests", to="marketplace.category")),
            ],
            options={"ordering": ["-created_at"], "verbose_name": "Коммерческий запрос", "verbose_name_plural": "Коммерческие запросы"},
        ),
        migrations.CreateModel(
            name="Offer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("delivery_days", models.PositiveIntegerField(default=1)),
                ("details", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="offers", to="marketplace.businessrequest")),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="offers", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["price", "created_at"], "verbose_name": "Предложение поставщика", "verbose_name_plural": "Предложения поставщиков"},
        ),
        migrations.AddConstraint(model_name="offer", constraint=models.UniqueConstraint(fields=("request", "supplier"), name="unique_offer_per_supplier_request")),
    ]
