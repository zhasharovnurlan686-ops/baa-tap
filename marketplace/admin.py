from django.contrib import admin
from .models import Category, BusinessRequest, Offer, SupplierListing, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "name_ky", "slug", "is_active")
    prepopulated_fields = {"slug": ("name_ru",)}
    list_filter = ("is_active",)

@admin.register(BusinessRequest)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("title", "buyer", "category", "city", "status", "created_at")
    list_filter = ("status", "category", "city")
    search_fields = ("title", "description", "buyer__username", "buyer__company_name")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("request", "supplier", "price", "delivery_days", "created_at")
    search_fields = ("request__title", "supplier__username", "supplier__company_name")
    readonly_fields = ("created_at", "updated_at")


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


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("title", "quantity", "unit_price", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "buyer", "supplier", "status", "total_amount", "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "buyer__username", "buyer__company_name",
        "supplier__username", "supplier__company_name",
    )
    readonly_fields = ("created_at", "updated_at", "total_amount")
    inlines = [OrderItemInline]
