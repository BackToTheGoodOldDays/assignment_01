from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for customer registration."""
    
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Customer
        fields = ['name', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return Customer.objects.create_user(**validated_data)


class CustomerLoginSerializer(serializers.Serializer):
    """Serializer for customer login."""
    
    email = serializers.EmailField()
    password = serializers.CharField()
