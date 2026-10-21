
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .models import Category, BusinessRequest, Offer
from .forms import RequestForm, OfferForm


def submission_rate_limited(request, action, limit=5, period=600):
    """Ограничивает частоту POST-запросов для авторизованного пользователя."""
    if request.method != "POST" or request.user.is_staff:
        return False

    key = f"baatap:submit:{action}:{request.user.pk}"
    count = cache.get(key, 0)

    if count >= limit:
        return True

    cache.set(key, count + 1, timeout=period)
    return False


def home(request):
    recent = (
        BusinessRequest.objects
        .filter(status=BusinessRequest.Status.OPEN)
        .select_related("category", "buyer")[:6]
    )
    categories = Category.objects.filter(is_active=True).annotate(
        request_count=Count(
            "requests",
            filter=Q(requests__status=BusinessRequest.Status.OPEN),
        )
    )
    open_count = BusinessRequest.objects.filter(
        status=BusinessRequest.Status.OPEN
    ).count()

    return render(request, "marketplace/home.html", {
        "recent_requests": recent,
        "categories": categories,
        "open_count": open_count,
    })


def request_list(request):
    qs = (
        BusinessRequest.objects
        .filter(status=BusinessRequest.Status.OPEN)
        .select_related("category", "buyer")
    )

    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    city = request.GET.get("city", "").strip()

    if query:
        qs = qs.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name_ru__icontains=query)
            | Q(category__name_ky__icontains=query)
        )

    if category.isdigit():
        qs = qs.filter(category_id=int(category))

    if city:
        qs = qs.filter(city__icontains=city)

    return render(request, "marketplace/request_list.html", {
        "requests": qs,
        "categories": Category.objects.filter(is_active=True),
        "q": query,
        "selected_category": category,
        "city": city,
    })


def request_detail(request, pk):
    item = get_object_or_404(
        BusinessRequest.objects.select_related("buyer", "category"),
        pk=pk,
    )
    offers = item.offers.select_related("supplier")

    my_offer = (
        offers.filter(supplier=request.user).first()
        if request.user.is_authenticated
        else None
    )

    can_view_offers = (
        request.user.is_authenticated
        and (request.user == item.buyer or request.user.is_staff)
    )

    return render(request, "marketplace/request_detail.html", {
        "item": item,
        "offers": offers if can_view_offers else [],
        "offer_count": offers.count(),
        "can_view_offers": can_view_offers,
        "my_offer": my_offer,
        "form": OfferForm(),
    })


@login_required
def request_create(request):
    if request.user.role not in ("buyer", "both") and not request.user.is_staff:
        messages.error(
            request,
            "Для создания запроса выберите роль покупателя или обе роли в профиле.",
        )
        return redirect("profile_edit")

    if submission_rate_limited(request, "request"):
        return HttpResponse(
            "Слишком много отправок. Попробуйте через 10 минут.",
            status=429,
        )

    form = RequestForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.buyer = request.user
        item.save()

        messages.success(request, "Запрос опубликован / Суроо жарыяланды")
        return redirect(item.get_absolute_url())

    return render(request, "marketplace/request_form.html", {
        "form": form,
        "page_title": "Создать коммерческий запрос / Коммерциялык суроо түзүү",
    })


@login_required
def request_edit(request, pk):
    item = get_object_or_404(
        BusinessRequest,
        pk=pk,
        buyer=request.user,
    )

    if submission_rate_limited(request, f"request-edit:{pk}"):
        return HttpResponse(
            "Слишком много отправок. Попробуйте через 10 минут.",
            status=429,
        )

    form = RequestForm(request.POST or None, instance=item)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Запрос обновлён / Суроо жаңыртылды")
        return redirect(item.get_absolute_url())

    return render(request, "marketplace/request_form.html", {
        "form": form,
        "page_title": "Редактировать запрос / Суроону өзгөртүү",
    })


@login_required
def offer_create(request, pk):
    item = get_object_or_404(
        BusinessRequest,
        pk=pk,
        status=BusinessRequest.Status.OPEN,
    )

    if item.buyer_id == request.user.id:
        messages.error(
            request,
            "Нельзя отправить предложение на собственный запрос.",
        )
        return redirect(item)

    if request.user.role not in ("supplier", "both") and not request.user.is_staff:
        messages.error(
            request,
            "Для отправки предложений выберите роль поставщика или обе роли в профиле.",
        )
        return redirect("profile_edit")

    if submission_rate_limited(request, f"offer:{pk}"):
        return HttpResponse(
            "Слишком много отправок. Попробуйте через 10 минут.",
            status=429,
        )

    existing = Offer.objects.filter(
        request=item,
        supplier=request.user,
    ).first()

    form = OfferForm(request.POST or None, instance=existing)

    if request.method == "POST" and form.is_valid():
        offer = form.save(commit=False)
        offer.request = item
        offer.supplier = request.user
        offer.save()

        messages.success(request, "Предложение отправлено / Сунуш жөнөтүлдү")
        return redirect(item)

    return render(request, "marketplace/offer_form.html", {
        "form": form,
        "item": item,
    })


@login_required
def dashboard(request):
    my_requests = (
        BusinessRequest.objects
        .filter(buyer=request.user)
        .select_related("category")
    )
    my_offers = (
        Offer.objects
        .filter(supplier=request.user)
        .select_related("request", "request__category")
    )

    return render(request, "dashboard/index.html", {
        "my_requests": my_requests,
        "my_offers": my_offers,
    })


def supplier_detail(request, username):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    supplier = get_object_or_404(
        User,
        username=username,
        role__in=["supplier", "both"],
    )

    return render(request, "accounts/supplier_detail.html", {
        "supplier": supplier,
        "offer_count": supplier.offers.count(),
    })
