from rest_framework import serializers
from .models import CartStatus, Cart, CartItem, SavedCart


class CartStatusSerializer(serializers.ModelSerializer):
    """Serializer for CartStatus model"""
    
    class Meta:
        model = CartStatus
        fields = ['status_id', 'name', 'description']


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model"""
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'item_id', 'cart', 'book_id', 'quantity', 
            'unit_price', 'subtotal', 'added_at', 'updated_at'
        ]
        read_only_fields = ['item_id', 'added_at', 'updated_at', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model with nested items"""
    items = CartItemSerializer(many=True, read_only=True)
    status = CartStatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=CartStatus.objects.all(),
        source='status',
        write_only=True,
        required=False
    )
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'cart_id', 'customer_id', 'status', 'status_id', 'is_active',
            'items', 'total_items', 'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['cart_id', 'created_at', 'updated_at', 'total_items', 'total_price']


class CartCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new cart"""
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=CartStatus.objects.all(),
        source='status',
        required=False
    )
    
    class Meta:
        model = Cart
        fields = ['cart_id', 'customer_id', 'status_id', 'is_active']
        read_only_fields = ['cart_id']
    
    def create(self, validated_data):
        # Set default status if not provided
        if 'status' not in validated_data:
            status, _ = CartStatus.objects.get_or_create(
                name='active',
                defaults={'description': 'Active shopping cart'}
            )
            validated_data['status'] = status
        return super().create(validated_data)


class SavedCartSerializer(serializers.ModelSerializer):
    """Serializer for SavedCart model"""
    
    class Meta:
        model = SavedCart
        fields = [
            'saved_id', 'customer_id', 'original_cart', 
            'cart_data', 'name', 'created_at'
        ]
        read_only_fields = ['saved_id', 'created_at']


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding an item to cart"""
    book_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(required=True, min_value=1)
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class CustomerCartCreateSerializer(serializers.Serializer):
    """Serializer for creating a cart for a customer (called by customer-service)"""
    customer_id = serializers.IntegerField(required=True)
    
    def validate_customer_id(self, value):
        if value < 1:
            raise serializers.ValidationError("Customer ID must be a positive integer")
        return value
