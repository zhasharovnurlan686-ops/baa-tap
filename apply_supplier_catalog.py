from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / f"backup_catalog_patch_{stamp}"

files = [
    "marketplace/models.py",
    "marketplace/forms.py",
    "marketplace/views.py",
    "marketplace/urls.py",
    "marketplace/admin.py",
    "templates/base.html",
]

for name in files:
    path = ROOT / name
    if path.exists():
        dest = backup / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

def read(name):
    return (ROOT / name).read_text(encoding="utf-8-sig")

def write(name, content):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

# 1. Supplier listing model
name = "marketplace/models.py"
s = read(name)
if "class SupplierListing(" not in s:
    s += '''

class SupplierListing(models.Model):
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="supplier_listings",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="supplier_listings",
    )
    title = models.CharField(max_length=180)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    quantity = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80, blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Объявление поставщика"
        verbose_name_plural = "Объявления поставщиков"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "supplier_listing_detail",
            kwargs={"pk": self.pk},
        )
'''
    write(name, s)
    print("OK: SupplierListing model added")
else:
    print("SKIP: SupplierListing model already exists")

# 2. Supplier listing form
name = "marketplace/forms.py"
s = read(name)
if "SupplierListingForm" not in s:
    s = s.replace(
        "from .models import BusinessRequest, Offer",
        "from .models import BusinessRequest, Offer, SupplierListing",
    )
    s += '''

class SupplierListingForm(forms.ModelForm):
    privacy_consent = forms.BooleanField(
        required=True,
        label=(
            "Я согласен(на) на обработку персональных данных "
            "и принимаю политику конфиденциальности."
        ),
    )

    class Meta:
        model = SupplierListing
        fields = (
            "category", "title", "description",
            "price", "quantity", "city", "image_url",
        )
        labels = {
            "category": "Категория",
            "title": "Название товара или услуги",
            "description": "Описание",
            "price": "Цена, сом",
            "quantity": "Количество или объём",
            "city": "Город",
            "image_url": "Ссылка на фотографию (необязательно)",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 5, "maxlength": 5000}
            ),
            "title": forms.TextInput(attrs={"maxlength": 180}),
            "quantity": forms.TextInput(attrs={"maxlength": 120}),
            "city": forms.TextInput(attrs={"maxlength": 80}),
            "image_url": forms.URLInput(
                attrs={"placeholder": "https://example.com/photo.jpg"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = (
            self.fields["category"].queryset.filter(is_active=True)
        )
'''
    write(name, s)
    print("OK: SupplierListingForm added")
else:
    print("SKIP: SupplierListingForm already exists")

# 3. Views
name = "marketplace/views.py"
s = read(name)
if "def supplier_listing_list(" not in s:
    s = s.replace(
        "from .models import Category, BusinessRequest, Offer",
        "from .models import Category, BusinessRequest, Offer, SupplierListing",
    )
    s = s.replace(
        "from .forms import RequestForm, OfferForm",
        "from .forms import RequestForm, OfferForm, SupplierListingForm",
    )
    s += '''

def supplier_listing_list(request):
    listings = (
        SupplierListing.objects
        .filter(
            is_active=True,
            supplier__role__in=["supplier", "both"],
        )
        .select_related("category", "supplier")
    )

    query = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()
    category = request.GET.get("category", "")

    if query:
        listings = listings.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name_ru__icontains=query)
            | Q(category__name_ky__icontains=query)
        )

    if city:
        listings = listings.filter(city__icontains=city)

    if category.isdigit():
        listings = listings.filter(category_id=int(category))

    return render(request, "marketplace/supplier_listing_list.html", {
        "listings": listings,
        "categories": Category.objects.filter(is_active=True),
        "q": query,
        "city": city,
        "selected_category": category,
    })


@login_required
def supplier_listing_create(request):
    if (
        request.user.role not in ("supplier", "both")
        and not request.user.is_staff
    ):
        messages.error(
            request,
            "Для публикации выберите роль поставщика "
            "или обе роли в профиле.",
        )
        return redirect("profile_edit")

    if submission_rate_limited(request, "supplier-listing"):
        return HttpResponse(
            "Слишком много отправок. Попробуйте через 10 минут.",
            status=429,
        )

    form = SupplierListingForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        listing = form.save(commit=False)
        listing.supplier = request.user
        listing.city = listing.city or request.user.city
        listing.save()
        messages.success(request, "Предложение поставщика опубликовано.")
        return redirect(listing.get_absolute_url())

    return render(request, "marketplace/supplier_listing_form.html", {
        "form": form,
        "page_title": "Разместить предложение",
    })


def supplier_listing_detail(request, pk):
    listing = get_object_or_404(
        SupplierListing.objects.select_related("category", "supplier"),
        pk=pk,
    )

    if not listing.is_active and (
        not request.user.is_authenticated
        or (
            request.user != listing.supplier
            and not request.user.is_staff
        )
    ):
        from django.http import Http404
        raise Http404

    return render(
        request,
        "marketplace/supplier_listing_detail.html",
        {"listing": listing},
    )
'''
    write(name, s)
    print("OK: supplier listing views added")
else:
    print("SKIP: supplier listing views already exist")

# 4. URLs
name = "marketplace/urls.py"
s = read(name)
if 'name="supplier_listing_list"' not in s:
    marker = "urlpatterns = ["
    if marker not in s:
        raise RuntimeError("Cannot find urlpatterns in marketplace/urls.py")
    s = s.replace(marker, marker + '''
    path("supplier-offers/", views.supplier_listing_list, name="supplier_listing_list"),
    path("supplier-offers/new/", views.supplier_listing_create, name="supplier_listing_create"),
    path("supplier-offers/<int:pk>/", views.supplier_listing_detail, name="supplier_listing_detail"),
''', 1)
    write(name, s)
    print("OK: supplier listing URLs added")
else:
    print("SKIP: supplier listing URLs already exist")

# 5. Admin
name = "marketplace/admin.py"
s = read(name)
if "SupplierListing" not in s:
    s = s.replace(
        "from .models import Category, BusinessRequest, Offer",
        "from .models import Category, BusinessRequest, Offer, SupplierListing",
    )
    s += '''

@admin.register(SupplierListing)
class SupplierListingAdmin(admin.ModelAdmin):
    list_display = (
        "title", "supplier", "category", "price",
        "city", "is_active", "created_at",
    )
    list_filter = ("is_active", "category", "city")
    search_fields = (
        "title", "description",
        "supplier__username", "supplier__company_name",
    )
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
'''
    write(name, s)
    print("OK: supplier listing admin added")
else:
    print("SKIP: SupplierListing already referenced in admin")

# 6. Templates
write("templates/marketplace/supplier_listing_list.html", '''{% extends "base.html" %}
{% block title %}Предложения поставщиков — BaaTap KG{% endblock %}
{% block content %}
<section class="page-hero">
  <div class="container">
    <div class="eyebrow">BaaTap KG / Каталог поставщиков</div>
    <h1>Предложения поставщиков</h1>
    <p>Находите товары и услуги, сравнивайте цены и связывайтесь с поставщиками.</p>
    {% if user.is_authenticated %}
      <a class="btn btn-primary" href="{% url 'supplier_listing_create' %}">Разместить предложение →</a>
    {% else %}
      <a class="btn btn-primary" href="{% url 'login' %}?next={% url 'supplier_listing_create' %}">Войти и разместить предложение →</a>
    {% endif %}
    <a class="btn btn-secondary" href="{% url 'request_list' %}">Заказы покупателей</a>
  </div>
</section>
<section class="section">
  <div class="container">
    <form class="filter-bar" method="get">
      <input type="search" name="q" value="{{ q }}" placeholder="Что ищете?">
      <select name="category">
        <option value="">Все категории</option>
        {% for c in categories %}
          <option value="{{ c.id }}" {% if selected_category == c.id|stringformat:"s" %}selected{% endif %}>{{ c.name_ru }}</option>
        {% endfor %}
      </select>
      <input name="city" value="{{ city }}" placeholder="Город">
      <button class="btn btn-primary" type="submit">Найти</button>
    </form>
    <div class="request-grid">
      {% for item in listings %}
        <article class="request-card">
          {% if item.image_url %}
            <img src="{{ item.image_url }}" alt="{{ item.title }}" loading="lazy" style="width:100%;max-height:220px;object-fit:cover;border-radius:12px">
          {% endif %}
          <div class="request-meta">
            <span class="pill">{{ item.category.localized_name: }}</span>
            <span>{{ item.created_at|date:"d.m.Y" }}</span>
          </div>
          <h3><a href="{{ item.get_absolute_url }}">{{ item.title }}</a></h3>
          <p>{{ item.description|truncatechars:180 }}</p>
          <p><strong>Поставщик:</strong>
            {{ item.supplier.company_name|default:item.supplier.get_full_name|default:item.supplier.username }}
          </p>
          <p><strong>Цена:</strong>
            {% if item.price != None %}{{ item.price|floatformat:"-2" }} сом{% else %}По договорённости{% endif %}
          </p>
          {% if item.quantity %}<p><strong>Количество:</strong> {{ item.quantity }}</p>{% endif %}
          <p><strong>Город:</strong> {{ item.city|default:"Кыргызстан" }}</p>
          <a class="btn btn-primary btn-block" href="{{ item.get_absolute_url }}">Подробнее →</a>
        </article>
      {% empty %}
        <div class="empty-state">Пока нет предложений поставщиков.</div>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
'''.replace("{{ item.category.localized_name: }}", "{{ item.category.name_ru }}"))

write("templates/marketplace/supplier_listing_form.html", '''{% extends "base.html" %}
{% block title %}{{ page_title }} — BaaTap KG{% endblock %}
{% block content %}
<section class="section">
  <div class="container form-page">
    <div class="form-card">
      <div class="eyebrow">BaaTap KG / Поставщикам</div>
      <h1>{{ page_title }}</h1>
      <p class="form-intro">Расскажите о товаре или услуге, укажите цену и количество.</p>
      <form method="post" class="styled-form">
        {% csrf_token %}
        {{ form.non_field_errors }}
        {% for field in form %}
          <div class="form-field">
            {% if field.name == "privacy_consent" %}
              <label for="{{ field.id_for_label }}">
                {{ field }} {{ field.label }}
                <a href="{% url 'privacy' %}" target="_blank" rel="noopener">Политика конфиденциальности</a>
              </label>
            {% else %}
              <label for="{{ field.id_for_label }}">{{ field.label }}</label>
              {{ field }}
            {% endif %}
            {% for error in field.errors %}<small class="error-text">{{ error }}</small>{% endfor %}
          </div>
        {% endfor %}
        <button class="btn btn-primary btn-block" type="submit">Опубликовать предложение →</button>
      </form>
    </div>
  </div>
</section>
{% endblock %}
''')

write("templates/marketplace/supplier_listing_detail.html", '''{% extends "base.html" %}
{% block title %}{{ listing.title }} — BaaTap KG{% endblock %}
{% block content %}
<section class="section">
  <div class="container form-page">
    <div class="form-card">
      <div class="eyebrow">{{ listing.category.name_ru }}</div>
      <h1>{{ listing.title }}</h1>
      {% if listing.image_url %}
        <img src="{{ listing.image_url }}" alt="{{ listing.title }}" style="width:100%;max-height:420px;object-fit:contain;border-radius:12px">
      {% endif %}
      <p>{{ listing.description|linebreaksbr }}</p>
      <p><strong>Поставщик:</strong>
        {{ listing.supplier.company_name|default:listing.supplier.get_full_name|default:listing.supplier.username }}
      </p>
      <p><strong>Цена:</strong>
        {% if listing.price != None %}{{ listing.price|floatformat:"-2" }} сом{% else %}По договорённости{% endif %}
      </p>
      {% if listing.quantity %}<p><strong>Количество:</strong> {{ listing.quantity }}</p>{% endif %}
      <p><strong>Город:</strong> {{ listing.city|default:listing.supplier.city|default:"Кыргызстан" }}</p>
      {% if listing.supplier.phone %}
        <a class="btn btn-primary" target="_blank" rel="noopener"
           href="https://wa.me/{{ listing.supplier.phone|cut:' '|cut:'+'|cut:'-'|cut:'('|cut:')' }}">
          Связаться с поставщиком в WhatsApp
        </a>
      {% else %}
        <p>Контактный телефон поставщика пока не указан.</p>
      {% endif %}
      <p><a href="{% url 'supplier_listing_list' %}">← Вернуться к каталогу</a></p>
    </div>
  </div>
</section>
{% endblock %}
''')

# 7. Add navigation link without replacing the existing links
name = "templates/base.html"
s = read(name)
if "supplier_listing_list" not in s:
    nav_start = s.find('<nav class="nav-links">')
    if nav_start == -1:
        print("WARNING: nav-links not found; add navigation link manually later")
    else:
        nav_end = s.find("</nav>", nav_start)
        if nav_end == -1:
            print("WARNING: closing nav tag not found")
        else:
            link = '''
            <a href="{% url 'supplier_listing_list' %}">
                {% if request.LANGUAGE_CODE == 'ky' %}Жеткирүүчүлөрдүн сунуштары{% else %}Предложения поставщиков{% endif %}
            </a>
'''
            s = s[:nav_end] + link + s[nav_end:]
            write(name, s)
            print("OK: navigation link added")
else:
    print("SKIP: supplier listing link already present")

print("\\nPatch complete.")
print("Backup:", backup)
