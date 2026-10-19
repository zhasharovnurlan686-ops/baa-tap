from marketplace import legal_views
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import set_language

urlpatterns = [
    path("privacy/", legal_views.privacy, name="privacy"),
    path("terms/", legal_views.terms, name="terms"),
    path("admin/", admin.site.urls),
    path("i18n/setlang/", set_language, name="set_language"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("marketplace.urls")),
]
