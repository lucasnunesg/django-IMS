from django.urls import path, include
from .views import inventory_list, per_product_view

urlpatterns = [
    path("", inventory_list, name='inventory_list'),
    path("per_product/<int:pk>", per_product_view, name='per_product')
]