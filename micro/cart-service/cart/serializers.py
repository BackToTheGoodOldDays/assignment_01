from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'book_id', 'book_title', 'book_author', 'book_price',
                  'quantity', 'subtotal', 'added_at']
        read_only_fields = ['id', 'added_at', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'items', 'total_items', 'total_price',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart."""
    
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    
    quantity = serializers.IntegerField(min_value=0)
