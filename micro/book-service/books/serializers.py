from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model."""
    
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'stock', 'description', 
                  'is_available', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookStockUpdateSerializer(serializers.Serializer):
    """Serializer for updating book stock."""
    
    quantity = serializers.IntegerField()
    operation = serializers.ChoiceField(choices=['increase', 'decrease'])
