import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer


@api_view(['GET', 'POST'])
def order_list(request):
    if request.method == 'GET':
        orders = Order.objects.prefetch_related('items').all()
        customer_id = request.query_params.get('customer_id')
        if customer_id:
            orders = orders.filter(customer_id=customer_id)
        return Response(OrderSerializer(orders, many=True).data)

    # POST - Create order
    data = request.data
    customer_id = data.get('customer_id')
    cart_id = data.get('cart_id')
    shipping_address = data.get('shipping_address', '')
    shipping_method_id = data.get('shipping_method_id')
    payment_method_id = data.get('payment_method_id')
    notes = data.get('notes', '')

    if not customer_id or not cart_id:
        return Response({'error': 'customer_id and cart_id required'}, status=400)

    # Get cart items
    try:
        cart_r = requests.get(f"{settings.CART_SERVICE_URL}/api/carts/{cart_id}/", timeout=5)
        if cart_r.status_code != 200:
            return Response({'error': 'Cart not found'}, status=400)
        cart_data = cart_r.json()
    except Exception as e:
        return Response({'error': f'Cannot reach cart-service: {str(e)}'}, status=503)

    cart_items = cart_data.get('items', [])
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=400)

    # Get shipping fee
    shipping_fee = Decimal('0')
    if shipping_method_id:
        try:
            ship_r = requests.get(f"{settings.SHIP_SERVICE_URL}/api/shipping-methods/{shipping_method_id}/", timeout=3)
            if ship_r.status_code == 200:
                shipping_fee = Decimal(str(ship_r.json().get('fee', 0)))
        except Exception:
            pass

    # Create order
    subtotal = sum(Decimal(str(item['unit_price'])) * item['quantity'] for item in cart_items)
    total = subtotal + shipping_fee

    order = Order.objects.create(
        order_number=Order.generate_order_number(),
        customer_id=customer_id,
        shipping_address=shipping_address,
        shipping_method_id=shipping_method_id,
        payment_method_id=payment_method_id,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total=total,
        notes=notes,
    )

    # Create order items
    for item in cart_items:
        book_title = item.get('book_title', f"Book #{item['book_id']}")
        OrderItem.objects.create(
            order=order,
            book_id=item['book_id'],
            book_title=book_title,
            quantity=item['quantity'],
            unit_price=Decimal(str(item['unit_price'])),
            subtotal=Decimal(str(item['unit_price'])) * item['quantity'],
        )

    # Reduce stock for each item
    for item in cart_items:
        try:
            requests.post(
                f"{settings.BOOK_SERVICE_URL}/api/books/{item['book_id']}/reduce_stock/",
                json={'quantity': item['quantity']},
                timeout=3
            )
        except Exception:
            pass

    # Deactivate cart
    try:
        requests.post(f"{settings.CART_SERVICE_URL}/api/carts/{cart_id}/deactivate/", timeout=3)
    except Exception:
        pass

    # Create payment
    if payment_method_id:
        try:
            requests.post(
                f"{settings.PAY_SERVICE_URL}/api/payments/",
                json={
                    'order_id': order.order_id,
                    'payment_method': payment_method_id,
                    'amount': str(total),
                },
                timeout=3
            )
        except Exception:
            pass

    # Create shipment
    if shipping_method_id:
        try:
            requests.post(
                f"{settings.SHIP_SERVICE_URL}/api/shipments/",
                json={
                    'order_id': order.order_id,
                    'shipping_method': shipping_method_id,
                },
                timeout=3
            )
        except Exception:
            pass

    return Response(OrderSerializer(order).data, status=201)


@api_view(['GET', 'PUT', 'DELETE'])
def order_detail(request, order_id):
    try:
        order = Order.objects.prefetch_related('items').get(order_id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

    if request.method == 'GET':
        return Response(OrderSerializer(order).data)
    elif request.method == 'DELETE':
        order.delete()
        return Response(status=204)

    # PUT - update status
    new_status = request.data.get('status')
    if new_status and new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
    return Response(OrderSerializer(order).data)


@api_view(['GET'])
def order_by_number(request, order_number):
    try:
        order = Order.objects.prefetch_related('items').get(order_number=order_number)
        return Response(OrderSerializer(order).data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)


@api_view(['POST'])
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

    if order.status in ('shipped', 'delivered'):
        return Response({'error': 'Cannot cancel order in current status'}, status=400)

    order.status = 'cancelled'
    order.save()
    return Response(OrderSerializer(order).data)
