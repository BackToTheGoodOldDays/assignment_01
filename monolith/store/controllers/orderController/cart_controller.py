"""
Cart controller - handles shopping cart operations.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from store.models.book.book import Book
from store.models.order.cart import Cart, CartItem, CartHistory, SavedCart


@login_required
def cart_view(request):
    """Display the shopping cart."""
    cart = Cart.get_or_create_active_cart(request.user)
    return render(request, 'cart/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, book_id):
    """Add a book to the cart."""
    if request.method == 'POST':
        book = get_object_or_404(Book, book_id=book_id)
        cart = Cart.get_or_create_active_cart(request.user)
        quantity = int(request.POST.get('quantity', 1))

        item, created = CartItem.objects.get_or_create(
            cart=cart, book=book,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        CartHistory.track_change(cart, 'add', item, f'Added {quantity} of {book.title}')
        messages.success(request, f'{book.title} added to cart.')

        if request.POST.get('buy_now'):
            return redirect('cart:checkout')
        return redirect('cart:view')
    return redirect('books:catalog')


@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    if request.method == 'POST':
        item = get_object_or_404(CartItem, item_id=item_id, cart__customer=request.user)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.update_quantity(quantity)
            CartHistory.track_change(item.cart, 'update', item, f'Updated quantity to {quantity}')
        else:
            item.delete()
            CartHistory.track_change(item.cart, 'remove', details=f'Removed item')
        messages.success(request, 'Cart updated.')
    return redirect('cart:view')


@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the cart."""
    if request.method == 'POST':
        item = get_object_or_404(CartItem, item_id=item_id, cart__customer=request.user)
        cart = item.cart
        item.delete()
        CartHistory.track_change(cart, 'remove', details='Item removed')
        messages.success(request, 'Item removed from cart.')
    return redirect('cart:view')


@login_required
def clear_cart(request):
    """Clear all items from the cart."""
    if request.method == 'POST':
        cart = Cart.get_or_create_active_cart(request.user)
        cart.items.all().delete()
        CartHistory.track_change(cart, 'clear', details='Cart cleared')
        messages.success(request, 'Cart cleared.')
    return redirect('cart:view')


@login_required
def save_cart(request):
    """Save the current cart for later."""
    if request.method == 'POST':
        cart = Cart.get_or_create_active_cart(request.user)
        name = request.POST.get('name', f'Saved Cart')
        items_data = []
        for item in cart.items.all():
            items_data.append({
                'book_id': item.book.book_id,
                'quantity': item.quantity,
            })
        SavedCart.objects.create(
            customer=request.user,
            original_cart=cart,
            name=name,
            cart_data={'items': items_data},
        )
        CartHistory.track_change(cart, 'save', details=f'Cart saved as "{name}"')
        messages.success(request, 'Cart saved!')
    return redirect('cart:view')


@login_required
def saved_carts(request):
    """Display saved carts."""
    carts = SavedCart.objects.filter(customer=request.user).order_by('-saved_date')
    return render(request, 'cart/saved_carts.html', {'saved_carts': carts})


@login_required
def restore_cart(request, saved_id):
    """Restore a saved cart."""
    if request.method == 'POST':
        saved = get_object_or_404(SavedCart, saved_cart_id=saved_id, customer=request.user)
        cart = saved.restore()
        CartHistory.track_change(cart, 'restore', details=f'Restored from "{saved.name}"')
        messages.success(request, f'Cart "{saved.name}" restored!')
    return redirect('cart:view')


@login_required
def delete_saved_cart(request, saved_id):
    """Delete a saved cart."""
    if request.method == 'POST':
        saved = get_object_or_404(SavedCart, saved_cart_id=saved_id, customer=request.user)
        saved.delete()
        messages.success(request, 'Saved cart deleted.')
    return redirect('cart:saved')


def cart_api(request):
    """API: Get cart info."""
    if not request.user.is_authenticated:
        return JsonResponse({'items': [], 'total': 0})
    cart = Cart.get_or_create_active_cart(request.user)
    items = [{
        'id': item.item_id,
        'book_id': item.book.book_id,
        'title': item.book.title,
        'quantity': item.quantity,
        'price': str(item.book.price),
        'subtotal': str(item.subtotal),
    } for item in cart.items.all()]
    return JsonResponse({'items': items, 'total': str(cart.calculate_total())})
