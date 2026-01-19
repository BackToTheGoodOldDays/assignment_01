from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Q
from .models import Book
from .serializers import BookSerializer, BookStockUpdateSerializer


class BookViewSet(viewsets.ModelViewSet):
    """ViewSet for Book CRUD operations."""
    
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_queryset(self):
        """Filter books by search query if provided."""
        queryset = Book.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__icontains=search)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update book stock (increase or decrease)."""
        book = self.get_object()
        serializer = BookStockUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            operation = serializer.validated_data['operation']
            
            if operation == 'decrease':
                if quantity > book.stock:
                    return Response(
                        {'error': f'Insufficient stock. Available: {book.stock}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                book.stock -= quantity
            else:
                book.stock += quantity
            
            book.save()
            return Response(BookSerializer(book).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def check_availability(self, request, pk=None):
        """Check if a book is available and return stock info."""
        book = self.get_object()
        return Response({
            'book_id': book.id,
            'title': book.title,
            'is_available': book.is_available,
            'stock': book.stock,
            'price': str(book.price)
        })


@api_view(['GET'])
def health_check(request):
    """Health check endpoint for the service."""
    return Response({'status': 'healthy', 'service': 'book-service'})
