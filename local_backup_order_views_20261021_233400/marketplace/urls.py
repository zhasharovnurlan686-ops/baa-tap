from django.urls import path
from . import views
urlpatterns = [
    path("supplier-offers/", views.supplier_listing_list, name="supplier_listing_list"),
    path("supplier-offers/new/", views.supplier_listing_create, name="supplier_listing_create"),
    path("supplier-offers/<int:pk>/", views.supplier_listing_detail, name="supplier_listing_detail"),

    path("", views.home, name="home"),
    path("requests/", views.request_list, name="request_list"),
    path("requests/new/", views.request_create, name="request_create"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/edit/", views.request_edit, name="request_edit"),
    path("requests/<int:pk>/offer/", views.offer_create, name="offer_create"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("supplier/<str:username>/", views.supplier_detail, name="supplier_detail"),
]
