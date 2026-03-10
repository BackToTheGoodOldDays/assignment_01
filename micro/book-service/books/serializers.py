from rest_framework import serializers
from .models import (
    BookStatus, BookTag, Book, BookImage,
    BookDescription, BookRating, BookInventory
)


class BookStatusSerializer(serializers.ModelSerializer):
    """Serializer for BookStatus model."""
    
    class Meta:
        model = BookStatus
        fields = ['status_id', 'status_name', 'description']


class BookTagSerializer(serializers.ModelSerializer):
    """Serializer for BookTag model."""
    
    class Meta:
        model = BookTag
        fields = ['tag_id', 'name', 'description']


class BookImageSerializer(serializers.ModelSerializer):
    """Serializer for BookImage model."""
    
    class Meta:
        model = BookImage
        fields = ['image_id', 'book', 'url', 'alt_text', 'is_primary', 'display_order']
        read_only_fields = ['image_id']


class BookDescriptionSerializer(serializers.ModelSerializer):
    """Serializer for BookDescription model."""
    
    class Meta:
        model = BookDescription
        fields = ['desc_id', 'book', 'content', 'short_description']
        read_only_fields = ['desc_id']


class BookRatingSerializer(serializers.ModelSerializer):
    """Serializer for BookRating model."""
    
    class Meta:
        model = BookRating
        fields = ['rating_id', 'book', 'avg_score', 'total_ratings']
        read_only_fields = ['rating_id', 'avg_score', 'total_ratings']


class BookRatingUpdateSerializer(serializers.Serializer):
    """Serializer for updating book rating."""
    score = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        min_value=0,
        max_value=5
    )


class BookInventorySerializer(serializers.ModelSerializer):
    """Serializer for BookInventory model."""
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = BookInventory
        fields = [
            'inventory_id', 'book', 'quantity', 'min_stock_level',
            'max_stock_level', 'reorder_point', 'last_restocked', 'stock_status'
        ]
        read_only_fields = ['inventory_id', 'last_restocked', 'stock_status']

    def get_stock_status(self, obj):
        return obj.check_stock()


class StockOperationSerializer(serializers.Serializer):
    """Serializer for stock operations (add/reduce)."""
    amount = serializers.IntegerField(min_value=1)


class BookListSerializer(serializers.ModelSerializer):
    """Serializer for listing books with basic info."""
    status = BookStatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=BookStatus.objects.all(),
        source='status',
        write_only=True
    )
    tags = BookTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=BookTag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False
    )
    primary_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'book_id', 'title', 'isbn', 'price', 'author_id',
            'category_id', 'publisher_id', 'status', 'status_id',
            'publication_date', 'pages', 'language', 'tags', 'tag_ids',
            'primary_image', 'in_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['book_id', 'created_at', 'updated_at']

    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return BookImageSerializer(primary).data
        return None

    def get_in_stock(self, obj):
        try:
            return obj.inventory.quantity > 0
        except BookInventory.DoesNotExist:
            return False


class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed book information with all related data."""
    status = BookStatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=BookStatus.objects.all(),
        source='status',
        write_only=True
    )
    tags = BookTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=BookTag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False
    )
    images = BookImageSerializer(many=True, read_only=True)
    description = BookDescriptionSerializer(read_only=True)
    rating = BookRatingSerializer(read_only=True)
    inventory = BookInventorySerializer(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'book_id', 'title', 'isbn', 'price', 'author_id',
            'category_id', 'publisher_id', 'status', 'status_id',
            'publication_date', 'pages', 'language', 'tags', 'tag_ids',
            'images', 'description', 'rating', 'inventory',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['book_id', 'created_at', 'updated_at']


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating books."""
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=BookTag.objects.all(),
        source='tags',
        many=True,
        required=False
    )
    
    class Meta:
        model = Book
        fields = [
            'book_id', 'title', 'isbn', 'price', 'author_id',
            'category_id', 'publisher_id', 'status', 'publication_date',
            'pages', 'language', 'tag_ids', 'created_at', 'updated_at'
        ]
        read_only_fields = ['book_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        book = Book.objects.create(**validated_data)
        book.tags.set(tags)
        
        # Create default inventory for new book
        BookInventory.objects.create(book=book)
        
        # Create default rating for new book
        BookRating.objects.create(book=book)
        
        return book

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags is not None:
            instance.tags.set(tags)
        
        return instance
