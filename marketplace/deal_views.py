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
