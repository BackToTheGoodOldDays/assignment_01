import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings
from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .models import Book, BookStatus, BookInventory
from .serializers import BookSerializer, BookStatusSerializer, BookInventorySerializer, BookCreateSerializer


class BookStatusViewSet(viewsets.ModelViewSet):
    queryset = BookStatus.objects.all()
    serializer_class = BookStatusSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('status', 'inventory').all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'isbn', 'description']
    ordering_fields = ['title', 'price', 'created_at', 'avg_rating']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return BookCreateSerializer
        return BookSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('category_id'):
            qs = qs.filter(category_id=params['category_id'])
        if params.get('author_id'):
            qs = qs.filter(author_id=params['author_id'])
        if params.get('publisher_id'):
            qs = qs.filter(publisher_id=params['publisher_id'])
        if params.get('min_price'):
            qs = qs.filter(price__gte=params['min_price'])
        if params.get('max_price'):
            qs = qs.filter(price__lte=params['max_price'])
        return qs

    @action(detail=True, methods=['get'])
    def full_details(self, request, pk=None):
        book = self.get_object()
        data = BookSerializer(book).data

        # Fetch author, category, publisher in parallel
        def fetch(url):
            try:
                r = requests.get(url, timeout=5)
                return r.json() if r.status_code == 200 else None
            except Exception:
                return None

        catalog = settings.CATALOG_SERVICE_URL
        urls = {
            'author':    f"{catalog}/api/authors/{book.author_id}/",
            'category':  f"{catalog}/api/categories/{book.category_id}/",
            'publisher': f"{catalog}/api/publishers/{book.publisher_id}/",
        }

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(fetch, url): key for key, url in urls.items()}
            for future in as_completed(futures):
                key = futures[future]
                result = future.result()
                if result:
                    data[key] = result

        return Response(data)

    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        book = self.get_object()
        quantity = request.data.get('quantity', 0)
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid quantity'}, status=400)
        inventory, _ = BookInventory.objects.get_or_create(book=book)
        inventory.quantity += quantity
        inventory.save()
        return Response({'book_id': book.book_id, 'new_quantity': inventory.quantity})

    @action(detail=True, methods=['post'])
    def reduce_stock(self, request, pk=None):
        book = self.get_object()
        quantity = request.data.get('quantity', 0)
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid quantity'}, status=400)
        try:
            inventory = book.inventory
        except BookInventory.DoesNotExist:
            return Response({'error': 'No inventory'}, status=400)
        if inventory.quantity < quantity:
            return Response({'error': 'Insufficient stock'}, status=400)
        inventory.quantity -= quantity
        inventory.save()
        return Response({'book_id': book.book_id, 'new_quantity': inventory.quantity})

    @action(detail=True, methods=['get'])
    def check_stock(self, request, pk=None):
        book = self.get_object()
        quantity = request.query_params.get('quantity', 1)
        try:
            inventory = book.inventory
            available = inventory.quantity >= int(quantity)
            return Response({'book_id': book.book_id, 'stock': inventory.quantity, 'available': available})
        except BookInventory.DoesNotExist:
            return Response({'book_id': book.book_id, 'stock': 0, 'available': False})

    @action(detail=False, methods=['post'])
    def bulk_check(self, request):
        """Check availability for multiple books. Payload: [{book_id, quantity}]"""
        items = request.data.get('items', [])
        result = []
        for item in items:
            bid = item.get('book_id')
            qty = item.get('quantity', 1)
            try:
                book = Book.objects.get(book_id=bid)
                try:
                    inv = book.inventory
                    available = inv.quantity >= int(qty)
                    result.append({'book_id': bid, 'available': available, 'stock': inv.quantity})
                except BookInventory.DoesNotExist:
                    result.append({'book_id': bid, 'available': False, 'stock': 0})
            except Book.DoesNotExist:
                result.append({'book_id': bid, 'available': False, 'error': 'Not found'})
        return Response(result)

    @action(detail=True, methods=['post'])
    def update_rating(self, request, pk=None):
        """Called by comment-rate-service to update book rating."""
        book = self.get_object()
        avg_rating = request.data.get('avg_rating')
        total_ratings = request.data.get('total_ratings')
        if avg_rating is not None:
            book.avg_rating = avg_rating
        if total_ratings is not None:
            book.total_ratings = total_ratings
        book.save()
        return Response({'book_id': book.book_id, 'avg_rating': str(book.avg_rating), 'total_ratings': book.total_ratings})
