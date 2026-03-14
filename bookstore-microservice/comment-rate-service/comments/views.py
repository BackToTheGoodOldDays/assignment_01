import requests
from django.conf import settings
from django.db.models import Avg, Count
from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer


def update_book_rating(book_id):
    """Call book-service to update avg rating."""
    stats = Review.objects.filter(book_id=book_id, is_approved=True).aggregate(
        avg_rating=Avg('rating'),
        total=Count('review_id')
    )
    avg = round(stats['avg_rating'] or 0, 2)
    total = stats['total'] or 0
    try:
        requests.post(
            f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/update_rating/",
            json={'avg_rating': avg, 'total_ratings': total},
            timeout=3
        )
    except Exception:
        pass


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        book_id = self.request.query_params.get('book_id')
        customer_id = self.request.query_params.get('customer_id')
        if book_id:
            qs = qs.filter(book_id=book_id)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return qs

    def perform_create(self, serializer):
        review = serializer.save()
        update_book_rating(review.book_id)

    def perform_update(self, serializer):
        review = serializer.save()
        update_book_rating(review.book_id)

    def perform_destroy(self, instance):
        book_id = instance.book_id
        instance.delete()
        update_book_rating(book_id)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.is_approved = True
        review.save()
        update_book_rating(review.book_id)
        return Response(ReviewSerializer(review).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        book_id = request.query_params.get('book_id')
        if not book_id:
            return Response({'error': 'book_id required'}, status=400)
        stats = Review.objects.filter(book_id=book_id, is_approved=True).aggregate(
            avg_rating=Avg('rating'),
            total=Count('review_id')
        )
        dist = {}
        for i in range(1, 6):
            dist[str(i)] = Review.objects.filter(book_id=book_id, rating=i, is_approved=True).count()
        return Response({
            'book_id': book_id,
            'avg_rating': round(stats['avg_rating'] or 0, 2),
            'total_reviews': stats['total'] or 0,
            'distribution': dist,
        })
