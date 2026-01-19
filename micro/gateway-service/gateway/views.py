"""
Gateway Views - Web interface that calls microservices.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .service_clients import customer_client, book_client, cart_client


def home(request):
    """Home page with featured books."""
    books = book_client.get_all_books()
    featured_books = books[:6] if books else []
    return render(request, 'home.html', {'featured_books': featured_books})


def book_list(request):
    """Display all books with search."""
    search_query = request.GET.get('search', '')
    books = book_client.get_all_books(search=search_query if search_query else None)
    
    if books is None:
        messages.error(request, 'Book service is unavailable. Please try again later.')
        books = []
    
    return render(request, 'books/book_list.html', {
        'books': books,
        'search_query': search_query
    })


def book_detail(request, book_id):
    """Display single book details."""
    book = book_client.get_book(book_id)
    
    if book is None:
        messages.error(request, 'Book not found or service unavailable.')
        return redirect('book_list')
    
    return render(request, 'books/book_detail.html', {'book': book})


def register(request):
    """Customer registration."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        result, status_code = customer_client.register(name, email, password, password_confirm)
        
        if status_code == 201:
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            error_msg = result.get('error', 'Registration failed.') if result else 'Service unavailable.'
            messages.error(request, error_msg)
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """Customer login."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        result, status_code = customer_client.login(email, password)
        
        if status_code == 200 and result:
            # Store customer info in session
            request.session['customer_id'] = result.get('customer_id')
            request.session['customer_name'] = result.get('name')
            request.session['customer_email'] = result.get('email')
            messages.success(request, f"Welcome back, {result.get('name')}!")
            return redirect('book_list')
        else:
            error_msg = result.get('error', 'Invalid credentials.') if result else 'Service unavailable.'
            messages.error(request, error_msg)
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """Customer logout."""
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def profile(request):
    """Customer profile page."""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.warning(request, 'Please login to view your profile.')
        return redirect('login')
    
    customer = customer_client.get_customer(customer_id)
    if customer is None:
        messages.error(request, 'Could not load profile.')
        return redirect('home')
    
    return render(request, 'accounts/profile.html', {'customer': customer})


def cart_view(request):
    """Display shopping cart."""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.warning(request, 'Please login to view your cart.')
        return redirect('login')
    
    cart_data = cart_client.get_cart(customer_id)
    
    if cart_data is None:
        messages.error(request, 'Cart service unavailable.')
        cart_data = {'items': [], 'total': 0}
    
    # Enrich cart items with book details
    items = cart_data.get('items', [])
    enriched_items = []
    total = 0
    
    for item in items:
        book = book_client.get_book(item['book_id'])
        if book:
            item['book'] = book
            item['subtotal'] = float(book['price']) * item['quantity']
            total += item['subtotal']
            enriched_items.append(item)
    
    return render(request, 'cart/cart.html', {
        'cart_items': enriched_items,
        'total': total
    })


def add_to_cart(request, book_id):
    """Add item to cart."""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.warning(request, 'Please login to add items to cart.')
        return redirect('login')
    
    quantity = int(request.POST.get('quantity', 1))
    result, status_code = cart_client.add_item(customer_id, book_id, quantity)
    
    if status_code in [200, 201]:
        messages.success(request, 'Item added to cart!')
    else:
        error_msg = result.get('error', 'Failed to add item.') if result else 'Service unavailable.'
        messages.error(request, error_msg)
    
    return redirect('book_list')


def update_cart(request, book_id):
    """Update cart item quantity."""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    quantity = int(request.POST.get('quantity', 1))
    cart_client.update_item(customer_id, book_id, quantity)
    messages.success(request, 'Cart updated!')
    return redirect('cart')


def remove_from_cart(request, book_id):
    """Remove item from cart."""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    cart_client.remove_item(customer_id, book_id)
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


def clear_cart(request):
    """Clear all items from cart."""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    cart_client.clear_cart(customer_id)
    messages.success(request, 'Cart cleared!')
    return redirect('cart')


def health_check(request):
    """Check health of all microservices."""
    status = {
        'gateway': 'healthy',
        'customer_service': 'unknown',
        'book_service': 'unknown',
        'cart_service': 'unknown'
    }
    
    if customer_client.health_check():
        status['customer_service'] = 'healthy'
    else:
        status['customer_service'] = 'unhealthy'
    
    if book_client.health_check():
        status['book_service'] = 'healthy'
    else:
        status['book_service'] = 'unhealthy'
    
    if cart_client.health_check():
        status['cart_service'] = 'healthy'
    else:
        status['cart_service'] = 'unhealthy'
    
    return JsonResponse(status)
