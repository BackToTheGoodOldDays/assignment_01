from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from books.models import Book


@login_required
def cart_view(request):
    """View for displaying the shopping cart."""
    cart = Cart.get_or_create_active_cart(request.user)
    return render(request, 'cart/cart.html', {'cart': cart})


@login_required
@require_POST
def add_to_cart(request, book_id):
    """Add a book to the shopping cart."""
    book = get_object_or_404(Book, id=book_id)
    cart = Cart.get_or_create_active_cart(request.user)
    
    # Check if book is in stock
    if not book.is_available:
        messages.error(request, f'Sorry, "{book.title}" is out of stock.')
        return redirect('books:catalog')
    
    # Get quantity from request
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if item already exists in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        book=book,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Update quantity if item already exists
        new_quantity = cart_item.quantity + quantity
        if new_quantity > book.stock:
            messages.warning(request, f'Only {book.stock} copies of "{book.title}" are available.')
            cart_item.quantity = book.stock
        else:
            cart_item.quantity = new_quantity
        cart_item.save()
        messages.success(request, f'Updated quantity of "{book.title}" in your cart.')
    else:
        messages.success(request, f'Added "{book.title}" to your cart.')
    
    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Added "{book.title}" to cart',
            'cart_total': cart.total_items
        })
    
    return redirect('cart:view')


@login_required
@require_POST
def update_cart_item(request, item_id):
    """Update quantity of a cart item."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.info(request, f'Removed "{cart_item.book.title}" from your cart.')
    elif quantity > cart_item.book.stock:
        messages.warning(request, f'Only {cart_item.book.stock} copies available.')
        cart_item.quantity = cart_item.book.stock
        cart_item.save()
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated successfully.')
    
    return redirect('cart:view')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove an item from the shopping cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    book_title = cart_item.book.title
    cart_item.delete()
    messages.info(request, f'Removed "{book_title}" from your cart.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = Cart.get_or_create_active_cart(request.user)
        return JsonResponse({
            'success': True,
            'message': f'Removed "{book_title}" from cart',
            'cart_total': cart.total_items
        })
    
    return redirect('cart:view')


@login_required
@require_POST
def clear_cart(request):
    """Clear all items from the shopping cart."""
    cart = Cart.get_or_create_active_cart(request.user)
    cart.items.all().delete()
    messages.info(request, 'Your cart has been cleared.')
    return redirect('cart:view')


@login_required
def cart_api(request):
    """API endpoint for cart data."""
    cart = Cart.get_or_create_active_cart(request.user)
    items = [{
        'id': item.id,
        'book_id': item.book.id,
        'book_title': item.book.title,
        'book_author': item.book.author,
        'quantity': item.quantity,
        'price': float(item.book.price),
        'subtotal': float(item.subtotal)
    } for item in cart.items.all()]
    
    return JsonResponse({
        'cart_id': cart.id,
        'items': items,
        'total_items': cart.total_items,
        'total_price': float(cart.total_price)
    })
