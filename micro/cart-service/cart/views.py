from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from decimal import Decimal
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer,
    AddToCartSerializer, UpdateCartItemSerializer
)
from .service_clients import CustomerServiceClient, BookServiceClient


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for Cart operations."""
    
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def get_queryset(self):
        """Filter carts by customer_id if provided."""
        queryset = Cart.objects.all()
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id, is_active=True)
        return queryset
    
    @action(detail=False, methods=['get', 'post'])
    def by_customer(self, request):
        """Get or create active cart for a customer."""
        customer_id = request.query_params.get('customer_id') or request.data.get('customer_id')
        
        if not customer_id:
            return Response(
                {'error': 'customer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create active cart
        cart, created = Cart.objects.get_or_create(
            customer_id=customer_id,
            is_active=True,
            defaults={'customer_id': customer_id}
        )
        
        return Response(CartSerializer(cart).data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add an item to the cart."""
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'customer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        book_id = serializer.validated_data['book_id']
        quantity = serializer.validated_data['quantity']
        
        # Get book info from book-service
        book_info = BookServiceClient.get_book(book_id)
        if not book_info:
            return Response(
                {'error': 'Book not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check availability
        if not book_info.get('is_available') or book_info.get('stock', 0) < quantity:
            return Response(
                {'error': 'Insufficient stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create cart
        cart, _ = Cart.objects.get_or_create(
            customer_id=customer_id,
            is_active=True,
            defaults={'customer_id': customer_id}
        )
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book_id,
            defaults={
                'book_title': book_info['title'],
                'book_author': book_info['author'],
                'book_price': Decimal(str(book_info['price'])),
                'quantity': quantity
            }
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > book_info.get('stock', 0):
                return Response(
                    {'error': f"Only {book_info.get('stock')} copies available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
        
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update cart item quantity."""
        customer_id = request.data.get('customer_id')
        book_id = request.data.get('book_id')
        
        if not customer_id or not book_id:
            return Response(
                {'error': 'customer_id and book_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UpdateCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        quantity = serializer.validated_data['quantity']
        
        try:
            cart = Cart.objects.get(customer_id=customer_id, is_active=True)
            cart_item = CartItem.objects.get(cart=cart, book_id=book_id)
            
            if quantity <= 0:
                cart_item.delete()
            else:
                # Check stock
                book_info = BookServiceClient.get_book(book_id)
                if book_info and quantity > book_info.get('stock', 0):
                    quantity = book_info.get('stock', 0)
                cart_item.quantity = quantity
                cart_item.save()
            
            return Response(CartSerializer(cart).data)
            
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {'error': 'Cart or item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove an item from the cart."""
        customer_id = request.data.get('customer_id')
        book_id = request.data.get('book_id')
        
        if not customer_id or not book_id:
            return Response(
                {'error': 'customer_id and book_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = Cart.objects.get(customer_id=customer_id, is_active=True)
            CartItem.objects.filter(cart=cart, book_id=book_id).delete()
            return Response(CartSerializer(cart).data)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from the cart."""
        customer_id = request.data.get('customer_id')
        
        if not customer_id:
            return Response(
                {'error': 'customer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = Cart.objects.get(customer_id=customer_id, is_active=True)
            cart.items.all().delete()
            return Response(CartSerializer(cart).data)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint for the service."""
    return Response({'status': 'healthy', 'service': 'cart-service'})
