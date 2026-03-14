"""
Order controller - handles checkout, orders, payments, shipping, etc.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from store.models.order.cart import Cart
from store.models.order.order import (
    Order, OrderItem, OrderStatus, OrderHistory, OrderTracking, OrderCancellation,
    Payment, PaymentMethod, PaymentStatus,
    Shipping, ShippingMethod, DeliveryAddress,
)
from store.models.book.book import Book
from store.models.review.review import Rating, Review


@login_required
def checkout(request):
    """Display checkout page."""
    cart = Cart.get_or_create_active_cart(request.user)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:view')

    subtotal = cart.calculate_total()
    tax = subtotal * 0  # No tax for now
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    addresses = DeliveryAddress.objects.filter(customer=request.user)

    return render(request, 'order/checkout.html', {
        'cart': cart,
        'subtotal': subtotal,
        'tax': tax,
        'shipping_methods': shipping_methods,
        'payment_methods': payment_methods,
        'addresses': addresses,
    })


@login_required
def create_order(request):
    """Create order from cart."""
    if request.method == 'POST':
        cart = Cart.get_or_create_active_cart(request.user)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart:view')

        # Get shipping/payment info
        shipping_method_id = request.POST.get('shipping_method')
        payment_method_id = request.POST.get('payment_method')
        address_id = request.POST.get('address_id')

        # Create order
        order = Order.place_order(customer=request.user, cart=cart)

        # Handle shipping
        shipping_method = None
        if shipping_method_id:
            shipping_method = ShippingMethod.objects.filter(method_id=shipping_method_id).first()

        delivery_address = None
        if address_id:
            delivery_address = DeliveryAddress.objects.filter(address_id=address_id, customer=request.user).first()
        else:
            # Create new address from form data
            recipient = request.POST.get('recipient_name', request.user.name)
            phone = request.POST.get('phone', request.user.phone or '')
            if recipient and phone:
                delivery_address = DeliveryAddress.objects.create(
                    customer=request.user,
                    recipient_name=recipient,
                    phone=phone,
                    address_line1=request.POST.get('address_line1', ''),
                    ward=request.POST.get('ward', ''),
                    district=request.POST.get('district', ''),
                    city=request.POST.get('city', ''),
                    postal_code=request.POST.get('postal_code', ''),
                )

        if shipping_method:
            shipping = Shipping.objects.create(
                order=order,
                method=shipping_method,
                delivery_address=delivery_address,
                fee=shipping_method.base_fee,
            )
            order.shipping_fee = shipping_method.base_fee
            order.total_price = order.subtotal + order.shipping_fee
            order.save()

        # Create payment
        if payment_method_id:
            payment_method = PaymentMethod.objects.filter(method_id=payment_method_id).first()
            if payment_method:
                Payment.objects.create(
                    order=order,
                    method=payment_method,
                    amount=order.total_price,
                    status=PaymentStatus.objects.filter(name='Pending').first(),
                )

        OrderHistory.track_status(order, 'Order created', new_status=order.status)
        messages.success(request, f'Order {order.order_number} created successfully!')
        return redirect('cart:detail', order_id=order.order_id)

    return redirect('cart:checkout')


@login_required
def order_list(request):
    """Display customer orders."""
    orders = Order.objects.filter(customer=request.user).select_related('status').prefetch_related('items')
    statuses = OrderStatus.objects.all()

    selected_status = request.GET.get('status')
    if selected_status:
        orders = orders.filter(status__name=selected_status)

    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    return render(request, 'order/orders.html', {
        'orders': orders,
        'statuses': statuses,
        'selected_status': selected_status,
        'is_paginated': orders.has_other_pages(),
        'page_obj': orders,
    })


@login_required
def order_detail(request, order_id):
    """Display order detail."""
    order = get_object_or_404(
        Order.objects.select_related('status', 'shipping__method', 'shipping__delivery_address')
        .prefetch_related('items__book__author', 'payments__method', 'payments__status', 'tracking'),
        order_id=order_id, customer=request.user
    )
    return render(request, 'order/order_detail.html', {'order': order})


@login_required
def process_payment(request, order_id):
    """Process payment for an order."""
    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=order_id, customer=request.user)
        payment = order.payments.first()
        if payment:
            payment.process_payment()
            OrderHistory.track_status(order, 'Payment processed')
            messages.success(request, 'Payment processed successfully!')
        else:
            messages.error(request, 'No payment found for this order.')
    return redirect('cart:detail', order_id=order_id)


@login_required
def track_order(request, order_id):
    """Track order status."""
    order = get_object_or_404(
        Order.objects.select_related('status', 'shipping__method')
        .prefetch_related('items', 'tracking'),
        order_id=order_id, customer=request.user
    )
    tracking = order.tracking.all()
    return render(request, 'order/track_order.html', {
        'order': order,
        'tracking': tracking,
    })


@login_required
def cancel_order(request, order_id):
    """Cancel an order."""
    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=order_id, customer=request.user)
        reason = request.POST.get('reason', 'Customer requested cancellation')
        cancellation = OrderCancellation.objects.create(
            order=order,
            reason=reason,
            requested_by=request.user,
            refund_amount=order.total_price,
        )
        cancellation.cancel_order()
        OrderHistory.track_status(order, 'Order cancelled', notes=reason)
        messages.success(request, f'Order {order.order_number} has been cancelled.')
    return redirect('cart:detail', order_id=order_id)


@login_required
def rate_book(request, order_id, book_id):
    """Rate a book from an order."""
    order = get_object_or_404(Order, order_id=order_id, customer=request.user)
    book = get_object_or_404(Book, book_id=book_id)

    if request.method == 'POST':
        score = int(request.POST.get('rating', 5))
        review_text = request.POST.get('review', '')

        rating, created = Rating.objects.update_or_create(
            customer=request.user, book=book,
            defaults={'score': score}
        )
        if review_text:
            Review.objects.update_or_create(
                customer=request.user, book=book,
                defaults={
                    'rating': rating,
                    'content': review_text,
                    'is_verified_purchase': True,
                }
            )
        messages.success(request, 'Thank you for your rating!')
        return redirect('cart:detail', order_id=order_id)

    return render(request, 'order/rate_book.html', {
        'book': book,
        'order_id': order_id,
    })


@login_required
def write_review(request, order_id, book_id):
    """Write a review for a book."""
    order = get_object_or_404(Order, order_id=order_id, customer=request.user)
    book = get_object_or_404(Book, book_id=book_id)

    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        score = int(request.POST.get('rating', 5))

        rating, _ = Rating.objects.update_or_create(
            customer=request.user, book=book,
            defaults={'score': score}
        )
        Review.objects.update_or_create(
            customer=request.user, book=book,
            defaults={
                'rating': rating,
                'title': title,
                'content': content,
                'is_verified_purchase': True,
            }
        )
        messages.success(request, 'Review submitted!')
        return redirect('books:detail', book_id=book_id)

    return render(request, 'order/write_review.html', {'book': book})


@login_required
def address_list(request):
    """Display customer delivery addresses."""
    addresses = DeliveryAddress.objects.filter(customer=request.user)
    return render(request, 'order/address_list.html', {'addresses': addresses})


@login_required
def add_address(request):
    """Add a new delivery address."""
    if request.method == 'POST':
        DeliveryAddress.objects.create(
            customer=request.user,
            recipient_name=request.POST.get('recipient_name', ''),
            phone=request.POST.get('phone', ''),
            address_line1=request.POST.get('detail', ''),
            ward=request.POST.get('ward', ''),
            district=request.POST.get('district', ''),
            city=request.POST.get('city', ''),
            is_default=request.POST.get('is_default') == 'on',
        )
        messages.success(request, 'Address added.')
        return redirect('cart:addresses')
    return render(request, 'order/add_address.html')


@login_required
def delete_address(request, address_id):
    """Delete a delivery address."""
    if request.method == 'POST':
        address = get_object_or_404(DeliveryAddress, address_id=address_id, customer=request.user)
        address.delete()
        messages.success(request, 'Address deleted.')
    return redirect('cart:addresses')


def orders_api(request):
    """API: List orders."""
    if not request.user.is_authenticated:
        return JsonResponse({'orders': []})
    orders = Order.objects.filter(customer=request.user)[:20]
    data = [{
        'id': o.order_id,
        'number': o.order_number,
        'status': str(o.status),
        'total': str(o.total_price),
    } for o in orders]
    return JsonResponse({'orders': data})


def shipping_methods_api(request):
    """API: List shipping methods."""
    methods = ShippingMethod.objects.filter(is_active=True)
    data = [{'id': m.method_id, 'name': m.name, 'fee': str(m.base_fee)} for m in methods]
    return JsonResponse({'methods': data})


def payment_methods_api(request):
    """API: List payment methods."""
    methods = PaymentMethod.objects.filter(is_active=True)
    data = [{'id': m.method_id, 'name': m.name, 'fee': str(m.processing_fee)} for m in methods]
    return JsonResponse({'methods': data})
