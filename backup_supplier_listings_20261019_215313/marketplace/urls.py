from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("requests/", views.request_list, name="request_list"),
    path("requests/new/", views.request_create, name="request_create"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/edit/", views.request_edit, name="request_edit"),
    path("requests/<int:pk>/offer/", views.offer_create, name="offer_create"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("supplier/<str:username>/", views.supplier_detail, name="supplier_detail"),
]
