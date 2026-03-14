import requests
from django.conf import settings


def call_service(url, method='get', data=None, params=None, headers=None, timeout=5):
    """Generic service call helper."""
    try:
        kwargs = {'timeout': timeout}
        if params:
            kwargs['params'] = params
        if headers:
            kwargs['headers'] = headers
        if data and method in ('post', 'put', 'patch'):
            kwargs['json'] = data
        resp = getattr(requests, method)(url, **kwargs)
        return resp.json(), resp.status_code
    except Exception as e:
        return {'error': str(e)}, 503


def get_books(search=None, category_id=None, page=1):
    params = {'page': page}
    if search:
        params['search'] = search
    if category_id:
        params['category_id'] = category_id
    return call_service(f"{settings.BOOK_SERVICE_URL}/api/books/", params=params)


def get_book(book_id):
    return call_service(f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/")


def get_author(author_id):
    return call_service(f"{settings.CATALOG_SERVICE_URL}/api/authors/{author_id}/")


def get_category(category_id):
    return call_service(f"{settings.CATALOG_SERVICE_URL}/api/categories/{category_id}/")


def get_publisher(publisher_id):
    return call_service(f"{settings.CATALOG_SERVICE_URL}/api/publishers/{publisher_id}/")


def get_categories():
    return call_service(f"{settings.CATALOG_SERVICE_URL}/api/categories/")


def get_cart(customer_id):
    return call_service(f"{settings.CART_SERVICE_URL}/api/carts/active-cart/?customer_id={customer_id}")


def add_to_cart(cart_id, book_id, quantity=1):
    data = {'cart_id': cart_id, 'book_id': book_id, 'quantity': quantity}
    return call_service(f"{settings.CART_SERVICE_URL}/api/cart-items/", 'post', data)


def get_orders(customer_id):
    return call_service(f"{settings.ORDER_SERVICE_URL}/api/orders/?customer_id={customer_id}")


def get_order(order_id):
    return call_service(f"{settings.ORDER_SERVICE_URL}/api/orders/{order_id}/")


def get_reviews(book_id):
    return call_service(f"{settings.COMMENT_SERVICE_URL}/api/reviews/?book_id={book_id}")


def get_shipping_methods():
    return call_service(f"{settings.SHIP_SERVICE_URL}/api/shipping-methods/")


def get_payment_methods():
    return call_service(f"{settings.PAY_SERVICE_URL}/api/payment-methods/")


def get_trending():
    return call_service(f"{settings.RECOMMENDER_SERVICE_URL}/api/trending/")


def register_customer(data):
    return call_service(f"{settings.CUSTOMER_SERVICE_URL}/api/customers/register/", 'post', data)


def login_customer(data):
    return call_service(f"{settings.CUSTOMER_SERVICE_URL}/api/customers/login/", 'post', data)


def login_staff(data):
    return call_service(f"{settings.STAFF_SERVICE_URL}/api/staff/login/", 'post', data)


def login_manager(data):
    return call_service(f"{settings.MANAGER_SERVICE_URL}/api/managers/login/", 'post', data)
