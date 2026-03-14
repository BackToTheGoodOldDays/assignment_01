import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


def get_book_info(book_id):
    """Fetch book info from book-service."""
    try:
        r = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@api_view(['POST'])
def create_for_customer(request):
    """Called by customer-service after registration."""
    customer_id = request.data.get('customer_id')
    if not customer_id:
        return Response({'error': 'customer_id required'}, status=400)
    # Don't create duplicate active carts
    if Cart.objects.filter(customer_id=customer_id, is_active=True).exists():
        cart = Cart.objects.get(customer_id=customer_id, is_active=True)
        return Response(CartSerializer(cart).data)
    cart = Cart.objects.create(customer_id=customer_id)
    return Response(CartSerializer(cart).data, status=201)


@api_view(['GET'])
def active_cart(request):
    """Get active cart for a customer."""
    customer_id = request.query_params.get('customer_id')
    if not customer_id:
        return Response({'error': 'customer_id required'}, status=400)
    try:
        cart = Cart.objects.get(customer_id=customer_id, is_active=True)
        return Response(CartSerializer(cart).data)
    except Cart.DoesNotExist:
        return Response({'error': 'No active cart found'}, status=404)


@api_view(['GET'])
def cart_detail(request, cart_id):
    try:
        cart = Cart.objects.get(cart_id=cart_id)
        return Response(CartSerializer(cart).data)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=404)


@api_view(['POST'])
def add_item(request, cart_id):
    try:
        cart = Cart.objects.get(cart_id=cart_id, is_active=True)
    except Cart.DoesNotExist:
        return Response({'error': 'Active cart not found'}, status=404)

    book_id = request.data.get('book_id')
    quantity = request.data.get('quantity', 1)

    if not book_id:
        return Response({'error': 'book_id required'}, status=400)

    # Validate book via book-service
    book = get_book_info(book_id)
    if not book:
        return Response({'error': 'Book not found'}, status=404)

    unit_price = book.get('price', 0)

    # Check stock
    try:
        stock_r = requests.get(
            f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/check_stock/",
            params={'quantity': quantity}, timeout=3
        )
        if stock_r.status_code == 200 and not stock_r.json().get('available', True) == False:
            pass
    except Exception:
        pass

    # Add or update item
    try:
        item = CartItem.objects.get(cart=cart, book_id=book_id)
        item.quantity += int(quantity)
        item.unit_price = unit_price
        item.save()
    except CartItem.DoesNotExist:
        item = CartItem.objects.create(
            cart=cart, book_id=book_id, quantity=quantity, unit_price=unit_price
        )

    return Response(CartItemSerializer(item).data, status=201)


@api_view(['PUT'])
def update_item(request, cart_id):
    try:
        cart = Cart.objects.get(cart_id=cart_id, is_active=True)
    except Cart.DoesNotExist:
        return Response({'error': 'Active cart not found'}, status=404)

    book_id = request.data.get('book_id')
    quantity = request.data.get('quantity')

    try:
        item = CartItem.objects.get(cart=cart, book_id=book_id)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)

    if int(quantity) <= 0:
        item.delete()
        return Response({'message': 'Item removed'})

    item.quantity = quantity
    item.save()
    return Response(CartItemSerializer(item).data)


@api_view(['DELETE'])
def remove_item(request, cart_id):
    try:
        cart = Cart.objects.get(cart_id=cart_id, is_active=True)
    except Cart.DoesNotExist:
        return Response({'error': 'Active cart not found'}, status=404)

    book_id = request.query_params.get('book_id') or request.data.get('book_id')
    if not book_id:
        return Response({'error': 'book_id required'}, status=400)

    CartItem.objects.filter(cart=cart, book_id=book_id).delete()
    return Response({'message': 'Item removed'})


@api_view(['DELETE'])
def clear_cart(request, cart_id):
    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=404)
    cart.items.all().delete()
    return Response({'message': 'Cart cleared'})


@api_view(['POST'])
def deactivate_cart(request, cart_id):
    """Called by order-service when order is placed."""
    try:
        cart = Cart.objects.get(cart_id=cart_id)
        cart.is_active = False
        cart.save()
        return Response({'message': 'Cart deactivated'})
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=404)


@api_view(['GET'])
def list_items(request):
    cart_id = request.query_params.get('cart_id')
    if not cart_id:
        return Response({'error': 'cart_id required'}, status=400)
    items = CartItem.objects.filter(cart_id=cart_id)
    # Enrich with book info
    result = []
    for item in items:
        item_data = CartItemSerializer(item).data
        book = get_book_info(item.book_id)
        if book:
            item_data['book_title'] = book.get('title', '')
            item_data['book_cover'] = book.get('cover_image_url', '')
        result.append(item_data)
    return Response(result)
