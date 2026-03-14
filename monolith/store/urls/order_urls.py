"""Cart and Order URL configuration."""
from django.urls import path
from store.controllers.orderController.cart_controller import (
    cart_view, add_to_cart, update_cart_item, remove_from_cart,
    clear_cart, save_cart, saved_carts, restore_cart, delete_saved_cart,
)
from store.controllers.orderController.order_controller import (
    order_list, order_detail, checkout, create_order,
    process_payment, track_order, cancel_order,
    rate_book, write_review,
    address_list, add_address, delete_address,
)

app_name = 'cart'

urlpatterns = [
    # Cart
    path('', cart_view, name='view'),
    path('add/<int:book_id>/', add_to_cart, name='add'),
    path('update/<int:item_id>/', update_cart_item, name='update'),
    path('remove/<int:item_id>/', remove_from_cart, name='remove'),
    path('clear/', clear_cart, name='clear'),
    path('save/', save_cart, name='save'),
    path('saved/', saved_carts, name='saved'),
    path('restore/<int:saved_id>/', restore_cart, name='restore'),
    path('delete-saved/<int:saved_id>/', delete_saved_cart, name='delete_saved'),

    # Checkout & Orders
    path('checkout/', checkout, name='checkout'),
    path('create/', create_order, name='create'),
    path('orders/', order_list, name='orders'),
    path('orders/<int:order_id>/', order_detail, name='detail'),
    path('orders/<int:order_id>/payment/', process_payment, name='payment'),
    path('orders/<int:order_id>/track/', track_order, name='track'),
    path('orders/<int:order_id>/cancel/', cancel_order, name='cancel'),

    # Ratings & Reviews
    path('orders/<int:order_id>/rate/<int:book_id>/', rate_book, name='rate_book'),
    path('orders/<int:order_id>/review/<int:book_id>/', write_review, name='write_review'),

    # Addresses
    path('addresses/', address_list, name='addresses'),
    path('addresses/add/', add_address, name='add_address'),
    path('addresses/<int:address_id>/delete/', delete_address, name='delete_address'),
]
