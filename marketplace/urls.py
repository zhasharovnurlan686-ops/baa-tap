from django.urls import path
from . import notification_views, views, order_views, deal_views
urlpatterns = [
    path("notifications/", notification_views.notification_list, name="notification_list"),
    path("notifications/<int:pk>/read/", notification_views.notification_read, name="notification_read"),
    path("requests/<int:pk>/offers/", deal_views.request_offers, name="request_offers"),
    path("offers/<int:pk>/accept/", deal_views.accept_offer, name="accept_offer"),
    path("orders/", order_views.order_list, name="order_list"),
    path("orders/<int:pk>/", order_views.order_detail, name="order_detail"),
    path("orders/<int:pk>/status/", order_views.order_update_status, name="order_update_status"),
    path("supplier-offers/<int:pk>/order/", order_views.order_create, name="order_create"),

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
