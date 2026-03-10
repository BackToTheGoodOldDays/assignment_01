from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, F
from django.shortcuts import get_object_or_404

from .models import (
    BookStatus, BookTag, Book, BookImage,
    BookDescription, BookRating, BookInventory
)
from .serializers import (
    BookStatusSerializer, BookTagSerializer, BookListSerializer,
    BookDetailSerializer, BookCreateUpdateSerializer, BookImageSerializer,
    BookDescriptionSerializer, BookRatingSerializer, BookRatingUpdateSerializer,
    BookInventorySerializer, StockOperationSerializer
)


class BookStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for managing book statuses."""
    queryset = BookStatus.objects.all()
    serializer_class = BookStatusSerializer
    lookup_field = 'status_id'


class BookTagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing book tags."""
    queryset = BookTag.objects.all()
    serializer_class = BookTagSerializer
    lookup_field = 'tag_id'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books with full CRUD operations.
    
    Supports:
    - Search by title, isbn, author_id, category_id
    - Filter by availability
    - Update rating endpoint
    - Get book details with all related info
    """
    queryset = Book.objects.select_related('status').prefetch_related('tags', 'images')
    lookup_field = 'book_id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'isbn']
    ordering_fields = ['title', 'price', 'publication_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        elif self.action == 'retrieve':
            return BookDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BookCreateUpdateSerializer
        return BookListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by title
        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)
        
        # Filter by ISBN
        isbn = self.request.query_params.get('isbn')
        if isbn:
            queryset = queryset.filter(isbn__icontains=isbn)
        
        # Filter by author_id
        author_id = self.request.query_params.get('author_id')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        # Filter by category_id
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by publisher_id
        publisher_id = self.request.query_params.get('publisher_id')
        if publisher_id:
            queryset = queryset.filter(publisher_id=publisher_id)
        
        # Filter by status
        status_id = self.request.query_params.get('status_id')
        if status_id:
            queryset = queryset.filter(status_id=status_id)
        
        # Filter by availability (in stock)
        available = self.request.query_params.get('available')
        if available is not None:
            if available.lower() in ('true', '1', 'yes'):
                queryset = queryset.filter(inventory__quantity__gt=0)
            elif available.lower() in ('false', '0', 'no'):
                queryset = queryset.filter(
                    Q(inventory__quantity=0) | Q(inventory__isnull=True)
                )
        
        # Filter by tag
        tag_id = self.request.query_params.get('tag_id')
        if tag_id:
            queryset = queryset.filter(tags__tag_id=tag_id)
        
        # Filter by language
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language__iexact=language)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset.distinct()

    @action(detail=True, methods=['post'])
    def update_rating(self, request, book_id=None):
        """Update the rating for a specific book."""
        book = self.get_object()
        serializer = BookRatingUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                rating = book.rating
            except BookRating.DoesNotExist:
                rating = BookRating.objects.create(book=book)
            
            rating.update_rating(serializer.validated_data['score'])
            return Response(BookRatingSerializer(rating).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def full_details(self, request, book_id=None):
        """Get complete book details with all related information."""
        book = self.get_object()
        serializer = BookDetailSerializer(book)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search endpoint.
        Supports: q (general search), title, isbn, author_id, category_id
        """
        queryset = self.get_queryset()
        
        # General search query
        q = request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(isbn__icontains=q) |
                Q(description__content__icontains=q) |
                Q(description__short_description__icontains=q)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = BookListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BookListSerializer(queryset, many=True)
        return Response(serializer.data)


class BookImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing book images."""
    queryset = BookImage.objects.select_related('book')
    serializer_class = BookImageSerializer
    lookup_field = 'image_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset

    @action(detail=True, methods=['post'])
    def set_primary(self, request, image_id=None):
        """Set this image as the primary image for its book."""
        image = self.get_object()
        # Reset other primary images for this book
        BookImage.objects.filter(book=image.book, is_primary=True).update(is_primary=False)
        image.is_primary = True
        image.save()
        return Response(BookImageSerializer(image).data)


class BookDescriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing book descriptions."""
    queryset = BookDescription.objects.select_related('book')
    serializer_class = BookDescriptionSerializer
    lookup_field = 'desc_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset


class BookRatingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing book ratings."""
    queryset = BookRating.objects.select_related('book')
    serializer_class = BookRatingSerializer
    lookup_field = 'rating_id'
    http_method_names = ['get', 'head', 'options']  # Read-only, updates via BookViewSet

    def get_queryset(self):
        queryset = super().get_queryset()
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset


class BookInventoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing book inventory.
    
    Provides:
    - Standard CRUD operations
    - add_stock action
    - reduce_stock action
    - check_stock action
    """
    queryset = BookInventory.objects.select_related('book')
    serializer_class = BookInventorySerializer
    lookup_field = 'inventory_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        
        # Filter by low stock
        low_stock = self.request.query_params.get('low_stock')
        if low_stock and low_stock.lower() in ('true', '1', 'yes'):
            queryset = queryset.filter(quantity__lte=F('min_stock_level'))
        
        # Filter by needs reorder
        needs_reorder = self.request.query_params.get('needs_reorder')
        if needs_reorder and needs_reorder.lower() in ('true', '1', 'yes'):
            queryset = queryset.filter(quantity__lte=F('reorder_point'))
        
        return queryset

    @action(detail=True, methods=['post'])
    def add_stock(self, request, inventory_id=None):
        """Add stock to inventory."""
        inventory = self.get_object()
        serializer = StockOperationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = inventory.add_stock(serializer.validated_data['amount'])
                return Response({
                    'message': f"Successfully added {serializer.validated_data['amount']} units",
                    'stock_status': result
                })
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reduce_stock(self, request, inventory_id=None):
        """Reduce stock from inventory."""
        inventory = self.get_object()
        serializer = StockOperationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = inventory.reduce_stock(serializer.validated_data['amount'])
                return Response({
                    'message': f"Successfully reduced {serializer.validated_data['amount']} units",
                    'stock_status': result
                })
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def check_stock(self, request, inventory_id=None):
        """Check stock status for an inventory item."""
        inventory = self.get_object()
        return Response(inventory.check_stock())

    @action(detail=False, methods=['get'])
    def low_stock_alerts(self, request):
        """Get all items with low stock or that need reordering."""
        low_stock_items = BookInventory.objects.filter(
            quantity__lte=F('reorder_point')
        ).select_related('book')
        
        serializer = BookInventorySerializer(low_stock_items, many=True)
        return Response({
            'count': low_stock_items.count(),
            'items': serializer.data
        })

    @action(detail=False, methods=['post'])
    def bulk_check(self, request):
        """Check stock for multiple books at once."""
        book_ids = request.data.get('book_ids', [])
        
        if not book_ids:
            return Response(
                {'error': 'book_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inventories = BookInventory.objects.filter(
            book_id__in=book_ids
        ).select_related('book')
        
        result = {
            inv.book_id: inv.check_stock() for inv in inventories
        }
        
        # Add books without inventory
        missing_books = set(book_ids) - set(result.keys())
        for book_id in missing_books:
            result[book_id] = {
                'book_id': book_id,
                'quantity': 0,
                'in_stock': False,
                'error': 'No inventory record found'
            }
        
        return Response(result)
