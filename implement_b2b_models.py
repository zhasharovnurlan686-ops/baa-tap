from pathlib import Path
from datetime import datetime
import re

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
model_path = Path("marketplace/models.py")
url_path = Path("marketplace/urls.py")

models = model_path.read_text(encoding="utf-8")
urls = url_path.read_text(encoding="utf-8")

# Не добавляем поля повторно.
if "business_request = models.ForeignKey(" not in models:
    match = re.search(r"(?m)^class Order\(models\.Model\):\s*$", models)
    if not match:
        raise SystemExit("Класс Order не найден.")
    pos = match.end()
    fields = '''

    business_request = models.ForeignKey(
        "BusinessRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Заявка покупателя",
    )
    offer = models.ForeignKey(
        "Offer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Коммерческое предложение",
    )
'''
    models = models[:pos] + fields + models[pos:]

# Статус коммерческого предложения.
offer_match = re.search(r"(?m)^class Offer\(models\.Model\):\s*$", models)
if not offer_match:
    raise SystemExit("Класс Offer не найден.")

offer_end = re.search(r"(?m)^class \w+", models[offer_match.end():])
offer_block_end = offer_match.end() + offer_end.start() if offer_end else len(models)
offer_block = models[offer_match.start():offer_block_end]

if re.search(r"(?m)^\s*status\s*=", offer_block) is None:
    status_field = '''

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Ожидает решения"),
            ("accepted", "Принято покупателем"),
            ("rejected", "Отклонено"),
        ],
        default="pending",
        verbose_name="Статус предложения",
    )
'''
    models = models[:offer_match.end()] + status_field + models[offer_match.end():]

backup = model_path.with_name(model_path.name + ".before_deal_" + stamp)
backup.write_bytes(model_path.read_bytes())
url_backup = url_path.with_name(url_path.name + ".before_deal_" + stamp)
url_backup.write_bytes(url_path.read_bytes())

model_path.write_text(models, encoding="utf-8")
print("Модели обновлены. Резервная копия:", backup)

# Добавляем страницу предложений и действие принятия.
if "request_offers" not in urls:
    urls = urls.replace(
        "urlpatterns = [",
        'urlpatterns = [\n'
        '    path("requests/<int:pk>/offers/", '
        'deal_views.request_offers, name="request_offers"),\n'
        '    path("offers/<int:pk>/accept/", '
        'deal_views.accept_offer, name="accept_offer"),',
        1,
    )
    urls = urls.replace(
        "from . import views, order_views",
        "from . import views, order_views, deal_views",
        1,
    )
    url_path.write_text(urls, encoding="utf-8")
    print("Маршруты предложений добавлены.")
else:
    print("Маршруты предложений уже присутствуют.")
