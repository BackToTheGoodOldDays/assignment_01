from concurrent.futures import ThreadPoolExecutor, as_completed
from django.shortcuts import render, redirect
from django.contrib import messages
from . import api_client


def home(request):
    books_data, _ = api_client.get_books()
    categories_data, _ = api_client.get_categories()
    trending_data, _ = api_client.get_trending()

    books = books_data if isinstance(books_data, list) else books_data.get('results', [])
    categories = categories_data if isinstance(categories_data, list) else []
    trending = trending_data.get('trending', []) if isinstance(trending_data, dict) else []

    return render(request, 'web/home.html', {
        'books': books[:12],
        'categories': categories,
        'trending': trending[:6],
    })


def book_list(request):
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    books_data, _ = api_client.get_books(search=search, category_id=category_id)
    categories_data, _ = api_client.get_categories()

    books = books_data if isinstance(books_data, list) else books_data.get('results', [])
    categories = categories_data if isinstance(categories_data, list) else []

    return render(request, 'web/books/list.html', {
        'books': books,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
    })


def book_detail(request, book_id):
    book_data, status = api_client.get_book(book_id)
    if status != 200:
        return render(request, 'web/error.html', {'message': 'Book not found'}, status=404)

    # Enrich with catalog data in parallel
    tasks = {}
    if book_data.get('author_id'):
        tasks['author'] = lambda aid=book_data['author_id']: api_client.get_author(aid)
    if book_data.get('category_id'):
        tasks['category'] = lambda cid=book_data['category_id']: api_client.get_category(cid)
    if book_data.get('publisher_id'):
        tasks['publisher'] = lambda pid=book_data['publisher_id']: api_client.get_publisher(pid)

    if tasks:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(fn): key for key, fn in tasks.items()}
            for future in as_completed(futures):
                key = futures[future]
                result, s = future.result()
                if s == 200:
                    book_data[key] = result

    reviews_data, _ = api_client.get_reviews(book_id)
    reviews = reviews_data if isinstance(reviews_data, list) else reviews_data.get('results', [])

    return render(request, 'web/books/detail.html', {
        'book': book_data,
        'reviews': reviews,
    })


def cart(request):
    customer = request.session.get('customer')
    if not customer:
        return redirect('/login/')

    cart_data, _ = api_client.get_cart(customer['customer_id'])
    return render(request, 'web/cart/cart.html', {'cart': cart_data})


def add_to_cart(request):
    if request.method != 'POST':
        return redirect('/')

    customer = request.session.get('customer')
    if not customer:
        return redirect(f"/login/?next={request.POST.get('next', '/')}")

    book_id = request.POST.get('book_id')
    quantity = int(request.POST.get('quantity', 1))
    next_url = request.POST.get('next', '/')

    # Get the customer's active cart
    cart_data, cart_status = api_client.get_cart(customer['customer_id'])
    if cart_status != 200 or not cart_data.get('cart_id'):
        messages.error(request, 'Could not find your cart. Please try again.')
        return redirect(next_url)

    cart_id = cart_data['cart_id']
    result, status = api_client.add_to_cart(cart_id, book_id, quantity)
    if status in (200, 201):
        messages.success(request, 'Added to cart!')
    else:
        error_msg = result.get('error') or result.get('detail') or 'Could not add to cart.'
        messages.error(request, error_msg)

    return redirect(next_url)


def checkout(request):
    customer = request.session.get('customer')
    if not customer:
        return redirect('/login/')

    shipping_methods, _ = api_client.get_shipping_methods()
    payment_methods, _ = api_client.get_payment_methods()
    cart_data, _ = api_client.get_cart(customer['customer_id'])

    if isinstance(shipping_methods, dict):
        shipping_methods = shipping_methods.get('results', [])
    if isinstance(payment_methods, dict):
        payment_methods = payment_methods.get('results', [])

    return render(request, 'web/cart/checkout.html', {
        'cart': cart_data,
        'shipping_methods': shipping_methods,
        'payment_methods': payment_methods,
    })


def order_list(request):
    customer = request.session.get('customer')
    if not customer:
        return redirect('/login/')

    orders_data, _ = api_client.get_orders(customer['customer_id'])
    orders = orders_data if isinstance(orders_data, list) else orders_data.get('results', [])

    return render(request, 'web/orders/list.html', {'orders': orders})


def order_detail(request, order_id):
    customer = request.session.get('customer')
    if not customer:
        return redirect('/login/')

    order_data, status = api_client.get_order(order_id)
    if status != 200:
        return render(request, 'web/error.html', {'message': 'Order not found'}, status=404)

    return render(request, 'web/orders/detail.html', {'order': order_data})


def login_view(request):
    if request.method == 'POST':
        data = {'email': request.POST.get('email'), 'password': request.POST.get('password')}
        result, status = api_client.login_customer(data)
        if status == 200:
            request.session['customer'] = result.get('customer')
            request.session['customer_token'] = result.get('token')
            return redirect('/')
        return render(request, 'web/auth/login.html', {'error': result.get('error', 'Login failed')})
    return render(request, 'web/auth/login.html')


def register_view(request):
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone', ''),
            'password': request.POST.get('password'),
        }
        result, status = api_client.register_customer(data)
        if status == 201:
            request.session['customer'] = result.get('customer')
            request.session['customer_token'] = result.get('token')
            return redirect('/')
        return render(request, 'web/auth/register.html', {'error': result.get('error', 'Registration failed')})
    return render(request, 'web/auth/register.html')


def logout_view(request):
    request.session.flush()
    return redirect('/')


def staff_login(request):
    if request.method == 'POST':
        data = {'username': request.POST.get('username'), 'password': request.POST.get('password')}
        result, status = api_client.login_staff(data)
        if status == 200:
            request.session['staff'] = result.get('staff')
            request.session['staff_token'] = result.get('token')
            return redirect('/staff/dashboard/')
        return render(request, 'web/staff/login.html', {'error': result.get('error', 'Login failed')})
    return render(request, 'web/staff/login.html')


def staff_dashboard(request):
    staff = request.session.get('staff')
    if not staff:
        return redirect('/staff/login/')

    books_data, _ = api_client.get_books()
    books = books_data if isinstance(books_data, list) else books_data.get('results', [])

    return render(request, 'web/staff/dashboard.html', {'staff': staff, 'books': books})


def manager_login(request):
    if request.method == 'POST':
        data = {'username': request.POST.get('username'), 'password': request.POST.get('password')}
        result, status = api_client.login_manager(data)
        if status == 200:
            request.session['manager'] = result.get('manager')
            request.session['manager_token'] = result.get('token')
            return redirect('/manager/dashboard/')
        return render(request, 'web/manager/login.html', {'error': result.get('error', 'Login failed')})
    return render(request, 'web/manager/login.html')


def manager_dashboard(request):
    manager = request.session.get('manager')
    if not manager:
        return redirect('/manager/login/')

    from django.conf import settings
    from . import api_client as ac

    dashboard_data, _ = ac.call_service(f"{settings.MANAGER_SERVICE_URL}/api/managers/dashboard/")

    return render(request, 'web/manager/dashboard.html', {
        'manager': manager,
        'dashboard': dashboard_data,
    })
