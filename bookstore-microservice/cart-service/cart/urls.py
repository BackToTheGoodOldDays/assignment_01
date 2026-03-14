from django.urls import path
from . import views

urlpatterns = [
    path('carts/create-for-customer/', views.create_for_customer),
    path('carts/active-cart/', views.active_cart),
    path('carts/<int:cart_id>/', views.cart_detail),
    path('carts/<int:cart_id>/add-item/', views.add_item),
    path('carts/<int:cart_id>/update-item/', views.update_item),
    path('carts/<int:cart_id>/remove-item/', views.remove_item),
    path('carts/<int:cart_id>/clear/', views.clear_cart),
    path('carts/<int:cart_id>/deactivate/', views.deactivate_cart),
    path('cart-items/', views.list_items),
]
