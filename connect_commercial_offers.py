from pathlib import Path
from datetime import datetime
import re

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def backup(path):
    p = Path(path)
    if p.exists():
        b = p.with_name(p.name + ".before_offer_flow_" + stamp)
        b.write_bytes(p.read_bytes())
        return b.name
    return None

model_path = Path("marketplace/models.py")
models = model_path.read_text(encoding="utf-8")

# Связываем заказ с коммерческим предложением и исходной заявкой.
order_match = re.search(r"(?m)^class Order\(models\.Model\):", models)
if not order_match:
    raise SystemExit("Не найден класс Order в marketplace/models.py")

order_end_match = re.search(r"(?m)^class \w+", models[order_match.end():])
order_end = order_match.end() + order_end_match.start() if order_end_match else len(models)
order_block = models[order_match.start():order_end]

new_order_fields = ""
if "business_request = models.ForeignKey(" not in order_block:
    new_order_fields += '''
    business_request = models.ForeignKey(
        "BusinessRequest", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="orders",
        verbose_name="Исходная заявка",
    )
'''
if "offer = models.ForeignKey(" not in order_block:
    new_order_fields += '''
    offer = models.ForeignKey(
        "Offer", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="orders",
        verbose_name="Коммерческое предложение",
    )
'''
if new_order_fields:
    models = models[:order_end] + new_order_fields + models[order_end:]

# Статус предложения.
offer_match = re.search(r"(?m)^class Offer\(models\.Model\):", models)
if not offer_match:
    raise SystemExit("Не найден класс Offer в marketplace/models.py")

next_class = re.search(r"(?m)^class \w+", models[offer_match.end():])
offer_end = offer_match.end() + next_class.start() if next_class else len(models)
offer_block = models[offer_match.start():offer_end]

if not re.search(r"(?m)^\s*status\s*=", offer_block):
    models = models[:offer_match.end()] + '''
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Ожидает решения"),
            ("accepted", "Принято"),
            ("rejected", "Отклонено"),
        ],
        default="pending",
        verbose_name="Статус предложения",
    )
''' + models[offer_match.end():]

if models != model_path.read_text(encoding="utf-8"):
    print("Резервная копия моделей:", backup(model_path))
    model_path.write_text(models, encoding="utf-8")
else:
    print("Поля связи уже существуют.")

# Создаём обработчики, адаптированные к именам полей моделей.
deal_code = r'''
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import BusinessRequest, Offer, Order


def _request_owner(business_request):
    for name in ("buyer", "author", "user", "created_by", "requester", "customer"):
        if hasattr(business_request, name):
            value = getattr(business_request, name)
            if value is not None:
                return value
    raise RuntimeError(
        "Не удалось определить владельца BusinessRequest. "
        "Проверьте поле пользователя в marketplace/models.py."
    )


def _field_names(model):
    return {field.name for field in model._meta.get_fields()}


def _status_value(model, desired):
    field_names = _field_names(model)
    if "status" not in field_names:
        return None
    field = model._meta.get_field("status")
    values = [value for value, label in (field.choices or [])]
    if desired in values:
        return desired
    aliases = {
        "new": ("new", "pending", "created"),
        "accepted": ("accepted", "approved"),
        "rejected": ("rejected", "declined"),
    }
    for candidate in aliases.get(desired, (desired,)):
        if candidate in values:
            return candidate
    return desired


@login_required
def request_offers(request, pk):
    business_request = get_object_or_404(BusinessRequest, pk=pk)
    owner = _request_owner(business_request)

    if not request.user.is_staff and owner.pk != request.user.pk:
        raise Http404

    offers = Offer.objects.filter(request=business_request).select_related("supplier")
    return render(request, "marketplace/request_offers.html", {
        "business_request": business_request,
        "offers": offers,
    })


@login_required
@require_POST
def accept_offer(request, pk):
    with transaction.atomic():
        offer = get_object_or_404(
            Offer.objects.select_for_update().select_related("request", "supplier"),
            pk=pk,
        )
        business_request = offer.request
        owner = _request_owner(business_request)

        if not request.user.is_staff and owner.pk != request.user.pk:
            raise Http404

        if offer.status != "pending":
            existing = Order.objects.filter(offer=offer).first()
            if existing:
                messages.info(request, "Заказ по этому предложению уже создан.")
                return redirect("order_detail", pk=existing.pk)
            messages.error(request, "Это предложение уже обработано.")
            return redirect("request_offers", pk=business_request.pk)

        if Order.objects.filter(offer=offer).exists():
            existing = Order.objects.get(offer=offer)
            return redirect("order_detail", pk=existing.pk)

        order_fields = _field_names(Order)
        kwargs = {}

        buyer_field = next(
            (name for name in ("buyer", "customer", "purchaser") if name in order_fields),
            None,
        )
        supplier_field = next(
            (name for name in ("supplier", "seller") if name in order_fields),
            None,
        )
        amount_field = next(
            (name for name in ("total_amount", "total", "amount", "price") if name in order_fields),
            None,
        )

        if not buyer_field or not supplier_field or not amount_field:
            raise RuntimeError(
                "Для создания заказа необходимы поля покупателя, поставщика и суммы в модели Order."
            )

        kwargs[buyer_field] = owner
        kwargs[supplier_field] = offer.supplier
        kwargs[amount_field] = offer.price

        if "status" in order_fields:
            kwargs["status"] = _status_value(Order, "new")
        if "business_request" in order_fields:
            kwargs["business_request"] = business_request
        if "offer" in order_fields:
            kwargs["offer"] = offer
        if "buyer_note" in order_fields:
            kwargs["buyer_note"] = (
                f"Создано из заявки №{business_request.pk}, "
                f"коммерческое предложение №{offer.pk}."
            )
        elif "note" in order_fields:
            kwargs["note"] = (
                f"Заявка №{business_request.pk}; предложение №{offer.pk}."
            )

        order = Order.objects.create(**kwargs)

        offer.status = _status_value(Offer, "accepted")
        offer.save(update_fields=["status"])

        for other in Offer.objects.select_for_update().filter(
            request=business_request, status="pending"
        ).exclude(pk=offer.pk):
            other.status = _status_value(Offer, "rejected")
            other.save(update_fields=["status"])

    messages.success(request, f"Предложение принято. Создан заказ №{order.pk}.")
    return redirect("order_detail", pk=order.pk)
'''

deal_path = Path("marketplace/deal_views.py")
backup(deal_path)
deal_path.write_text(deal_code.lstrip(), encoding="utf-8")
print("Обработчики коммерческих предложений подключены.")

# Подключаем URL.
url_path = Path("marketplace/urls.py")
urls = url_path.read_text(encoding="utf-8")
if "from . import views, order_views, deal_views" not in urls:
    print("Резервная копия URL:", backup(url_path))
    if "from . import views, order_views" in urls:
        urls = urls.replace(
            "from . import views, order_views",
            "from . import views, order_views, deal_views",
            1,
        )
    elif "from . import views" in urls:
        urls = urls.replace("from . import views", "from . import views, deal_views", 1)
    else:
        urls = "from . import deal_views\n" + urls

if 'name="request_offers"' not in urls:
    urls = urls.replace(
        "urlpatterns = [",
        'urlpatterns = [\n'
        '    path("requests/<int:pk>/offers/", deal_views.request_offers, name="request_offers"),\n'
        '    path("offers/<int:pk>/accept/", deal_views.accept_offer, name="accept_offer"),',
        1,
    )
    url_path.write_text(urls, encoding="utf-8")
    print("Маршруты подключены.")

# Страница предложений.
template_path = Path("templates/marketplace/request_offers.html")
template_path.parent.mkdir(parents=True, exist_ok=True)
backup(template_path)
template_path.write_text('''{% extends "base.html" %}
{% block title %}Коммерческие предложения — BaaTap KG{% endblock %}
{% block content %}
<section class="section">
  <div class="container">
    <a href="{% url 'request_detail' business_request.pk %}">← Вернуться к заявке</a>
    <h1>Коммерческие предложения</h1>
    <div class="dashboard-panel">
      <h2>{{ business_request.title }}</h2>
      <p>{{ business_request.description }}</p>
      {% for offer in offers %}
      <div class="dashboard-row">
        <div>
          <strong>{{ offer.supplier.company_name|default:offer.supplier.username }}</strong>
          <p>Цена: {{ offer.price|floatformat:2 }} сом</p>
          <p>Срок поставки: {{ offer.delivery_days }} дн.</p>
          <p>{{ offer.details|default:"Условия не указаны" }}</p>
          <p>Статус: {{ offer.get_status_display|default:offer.status }}</p>
        </div>
        {% if offer.status == "pending" %}
        <form method="post" action="{% url 'accept_offer' offer.pk %}">
          {% csrf_token %}
          <button class="btn btn-primary" type="submit">Принять и создать заказ</button>
        </form>
        {% endif %}
      </div>
      {% empty %}
      <p>Поставщики ещё не отправили предложения.</p>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
''', encoding="utf-8")
print("Страница предложений обновлена.")

# Добавляем ссылку на предложения в карточку заявки.
detail_path = Path("templates/marketplace/request_detail.html")
if detail_path.exists():
    detail = detail_path.read_text(encoding="utf-8")
    if "name='request_offers'" not in detail and 'name="request_offers"' not in detail:
        backup(detail_path)
        addition = '''
{% if item %}
<div class="dashboard-panel" style="margin-top:20px">
  <h3>Коммерческие предложения</h3>
  <a class="btn btn-primary" href="{% url 'request_offers' item.pk %}">Посмотреть предложения</a>
</div>
{% elif business_request %}
<div class="dashboard-panel" style="margin-top:20px">
  <h3>Коммерческие предложения</h3>
  <a class="btn btn-primary" href="{% url 'request_offers' business_request.pk %}">Посмотреть предложения</a>
</div>
{% endif %}
'''
        detail = detail.replace("{% endblock %}", addition + "\n{% endblock %}", 1)
        detail_path.write_text(detail, encoding="utf-8")
        print("Ссылка на предложения добавлена в карточку заявки.")

print("Изменения кода внесены.")
