from django.urls import path
from management.views import *
from . import views
from rest_framework import routers


urlpatterns = [
    path("user/register", UserRegistrationView.as_view(), name="register"),
    path("user/login", UserLoginView.as_view(), name="login"),
    path("vendors", VendorView.as_view(), name="vendors"),
    path("vendors/<int:pk>", VendorView.as_view(), name="vendors"),
    path('vendors/<int:pk>/performance', VendorPerformanceView.as_view(), name='vendor-performance'),
    path("purchase_orders", PurchaseOrderView.as_view(), name="purchase_orders"),
    path("purchase_orders/<int:pk>", PurchaseOrderView.as_view(), name="purchase_orders"),
    path("purchase_orders/<int:po_id>/acknowledge", AcknowledgePurchaseOrder.as_view(), name="acknowledge-purchase-order"),

]
