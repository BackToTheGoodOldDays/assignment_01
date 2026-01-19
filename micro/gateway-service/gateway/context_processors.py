"""Context processors for gateway templates."""
from .service_clients import cart_client


def cart_count(request):
    """Add cart item count to all templates."""
    count = 0
    customer_id = request.session.get('customer_id')
    if customer_id:
        try:
            cart_data = cart_client.get_cart(customer_id)
            if cart_data and 'items' in cart_data:
                count = len(cart_data['items'])
        except:
            pass
    return {'cart_count': count}
