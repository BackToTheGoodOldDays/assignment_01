from rest_framework import serializers
from .models import Book, BookStatus, BookInventory


class BookStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookStatus
        fields = '__all__'


class BookInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInventory
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    inventory = BookInventorySerializer(read_only=True)
    status_name = serializers.CharField(source='status.status_name', read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class BookCreateSerializer(serializers.ModelSerializer):
    initial_stock = serializers.IntegerField(write_only=True, required=False, default=0)

    class Meta:
        model = Book
        fields = ['title', 'isbn', 'price', 'author_id', 'category_id', 'publisher_id',
                  'language', 'pages', 'description', 'cover_image_url', 'publication_year',
                  'status', 'initial_stock']

    def create(self, validated_data):
        initial_stock = validated_data.pop('initial_stock', 0)
        book = Book.objects.create(**validated_data)
        BookInventory.objects.create(book=book, quantity=initial_stock)
        return book
