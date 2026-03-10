from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import CartStatus, Cart, CartItem, SavedCart
from .serializers import (
    CartStatusSerializer,
    CartSerializer,
    CartCreateSerializer,
    CartItemSerializer,
    SavedCartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    CustomerCartCreateSerializer
)
from .services import book_service_client


class CartStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for CartStatus CRUD operations"""
    queryset = CartStatus.objects.all()
    serializer_class = CartStatusSerializer
    lookup_field = 'status_id'


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for Cart CRUD operations with additional cart actions"""
    queryset = Cart.objects.all()
    lookup_field = 'cart_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CartCreateSerializer
        return CartSerializer
    
    def get_queryset(self):
        queryset = Cart.objects.all()
        customer_id = self.request.query_params.get('customer_id')
        is_active = self.request.query_params.get('is_active')
        
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if is_active is not None:
            is_active_bool = is_active.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_active=is_active_bool)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, cart_id=None):
        """Add an item to the cart"""
        cart = self.get_object()
        serializer = AddToCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        book_id = serializer.validated_data['book_id']
        quantity = serializer.validated_data['quantity']
        
        # Verify book availability
        is_available, book_data, message = book_service_client.verify_book_availability(
            book_id, quantity
        )
        
        if not is_available and book_data is None:
            # If we can't connect to book service, allow adding with default price
            # In production, you might want to handle this differently
            unit_price = Decimal('0.00')
        elif not is_available:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            unit_price = Decimal(str(book_data.get('price', '0.00')))
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book_id,
            defaults={'quantity': quantity, 'unit_price': unit_price}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.unit_price = unit_price  # Update price in case it changed
            cart_item.save()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put', 'patch'], url_path='update_item/(?P<item_id>[^/.]+)')
    def update_item(self, request, cart_id=None, item_id=None):
        """Update cart item quantity"""
        cart = self.get_object()
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
        
        serializer = UpdateCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_quantity = serializer.validated_data['quantity']
        
        # Verify book availability for new quantity
        is_available, book_data, message = book_service_client.verify_book_availability(
            cart_item.book_id, new_quantity
        )
        
        if not is_available and book_data is not None:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = new_quantity
        cart_item.save()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], url_path='remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, cart_id=None, item_id=None):
        """Remove an item from the cart"""
        cart = self.get_object()
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
        cart_item.delete()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def clear(self, request, cart_id=None):
        """Clear all items from the cart"""
        cart = self.get_object()
        cart.items.all().delete()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def save_cart(self, request, cart_id=None):
        """Save the current cart for later"""
        cart = self.get_object()
        
        # Prepare cart data as JSON
        cart_items_data = [
            {
                'book_id': item.book_id,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price)
            }
            for item in cart.items.all()
        ]
        
        name = request.data.get('name', f'Saved Cart from {cart.created_at.strftime("%Y-%m-%d")}')
        
        saved_cart = SavedCart.objects.create(
            customer_id=cart.customer_id,
            original_cart=cart,
            cart_data={'items': cart_items_data},
            name=name
        )
        
        serializer = SavedCartSerializer(saved_cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ModelViewSet):
    """ViewSet for CartItem CRUD operations"""
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    lookup_field = 'item_id'
    
    def get_queryset(self):
        queryset = CartItem.objects.all()
        cart_id = self.request.query_params.get('cart_id')
        book_id = self.request.query_params.get('book_id')
        
        if cart_id:
            queryset = queryset.filter(cart_id=cart_id)
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        
        return queryset


class SavedCartViewSet(viewsets.ModelViewSet):
    """ViewSet for SavedCart CRUD operations"""
    queryset = SavedCart.objects.all()
    serializer_class = SavedCartSerializer
    lookup_field = 'saved_id'
    
    def get_queryset(self):
        queryset = SavedCart.objects.all()
        customer_id = self.request.query_params.get('customer_id')
        
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def restore_cart(self, request, saved_id=None):
        """Restore a saved cart to a new active cart"""
        saved_cart = self.get_object()
        
        # Get or create default status
        active_status, _ = CartStatus.objects.get_or_create(
            name='active',
            defaults={'description': 'Active shopping cart'}
        )
        
        # Deactivate existing active carts for this customer
        Cart.objects.filter(
            customer_id=saved_cart.customer_id,
            is_active=True
        ).update(is_active=False)
        
        # Create new cart
        new_cart = Cart.objects.create(
            customer_id=saved_cart.customer_id,
            status=active_status,
            is_active=True
        )
        
        # Restore items from saved cart data
        cart_data = saved_cart.cart_data
        items = cart_data.get('items', [])
        
        for item_data in items:
            CartItem.objects.create(
                cart=new_cart,
                book_id=item_data['book_id'],
                quantity=item_data['quantity'],
                unit_price=Decimal(item_data['unit_price'])
            )
        
        cart_serializer = CartSerializer(new_cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_for_customer(request):
    """
    Create a new active cart for a customer.
    This endpoint is called by customer-service during registration.
    """
    serializer = CustomerCartCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    customer_id = serializer.validated_data['customer_id']
    
    # Get or create default active status
    active_status, _ = CartStatus.objects.get_or_create(
        name='active',
        defaults={'description': 'Active shopping cart'}
    )
    
    # Check if customer already has an active cart
    existing_cart = Cart.objects.filter(
        customer_id=customer_id,
        is_active=True
    ).first()
    
    if existing_cart:
        cart_serializer = CartSerializer(existing_cart)
        return Response(
            {
                'message': 'Customer already has an active cart',
                'cart': cart_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    # Create new cart for customer
    new_cart = Cart.objects.create(
        customer_id=customer_id,
        status=active_status,
        is_active=True
    )
    
    cart_serializer = CartSerializer(new_cart)
    return Response(
        {
            'message': 'Cart created successfully',
            'cart': cart_serializer.data
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
def get_active_cart(request):
    """
    Get the active cart for a customer.
    Query parameter: customer_id (required)
    """
    customer_id = request.query_params.get('customer_id')
    
    if not customer_id:
        return Response(
            {'error': 'customer_id query parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        customer_id = int(customer_id)
    except ValueError:
        return Response(
            {'error': 'customer_id must be a valid integer'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart = Cart.objects.filter(
        customer_id=customer_id,
        is_active=True
    ).first()
    
    if not cart:
        return Response(
            {'error': 'No active cart found for this customer'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)
