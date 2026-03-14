import requests
from django.conf import settings
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserInteraction
from .serializers import UserInteractionSerializer


def get_books(book_ids, limit=10):
    """Fetch multiple books from book-service."""
    books = []
    for bid in book_ids[:limit]:
        try:
            r = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/{bid}/", timeout=2)
            if r.status_code == 200:
                books.append(r.json())
        except Exception:
            pass
    return books


@api_view(['POST'])
def log_interaction(request):
    serializer = UserInteractionSerializer(data=request.data)
    if serializer.is_valid():
        interaction = serializer.save()
        return Response(UserInteractionSerializer(interaction).data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
def recommendations(request, customer_id):
    """Recommend books based on what customer has interacted with + popular books."""
    # Get books this customer has interacted with
    interacted = UserInteraction.objects.filter(customer_id=customer_id).values_list('book_id', flat=True)

    # Get popular books that customer hasn't interacted with
    popular_book_ids = (
        UserInteraction.objects
        .exclude(book_id__in=interacted)
        .values('book_id')
        .annotate(score=Count('interaction_id'))
        .order_by('-score')
        .values_list('book_id', flat=True)[:20]
    )

    # If not enough, fetch from book-service directly
    if len(popular_book_ids) < 5:
        try:
            r = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/?ordering=-avg_rating", timeout=3)
            if r.status_code == 200:
                api_books = r.json()
                if isinstance(api_books, dict) and 'results' in api_books:
                    api_books = api_books['results']
                return Response({
                    'customer_id': customer_id,
                    'recommendations': api_books[:10],
                    'algorithm': 'popular_fallback'
                })
        except Exception:
            pass
        return Response({'customer_id': customer_id, 'recommendations': [], 'algorithm': 'no_data'})

    books = get_books(list(popular_book_ids))
    return Response({'customer_id': customer_id, 'recommendations': books, 'algorithm': 'collaborative'})


@api_view(['GET'])
def trending(request):
    """Most interacted books in last 30 days."""
    from datetime import timedelta
    from django.utils import timezone

    since = timezone.now() - timedelta(days=30)
    trending_ids = (
        UserInteraction.objects
        .filter(created_at__gte=since)
        .values('book_id')
        .annotate(count=Count('interaction_id'))
        .order_by('-count')
        .values_list('book_id', flat=True)[:20]
    )

    if not trending_ids:
        # Fallback: top rated books
        try:
            r = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/?ordering=-avg_rating", timeout=3)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    data = data.get('results', [])
                return Response({'trending': data[:10], 'source': 'top_rated_fallback'})
        except Exception:
            pass
        return Response({'trending': [], 'source': 'no_data'})

    books = get_books(list(trending_ids))
    return Response({'trending': books, 'source': 'interactions'})


@api_view(['GET'])
def best_rated(request):
    """Best rated books from book-service."""
    try:
        r = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/?ordering=-avg_rating", timeout=3)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                data = data.get('results', [])
            return Response({'best_rated': data[:10]})
    except Exception:
        pass
    return Response({'best_rated': [], 'error': 'Book service unavailable'})


@api_view(['GET'])
def similar_books(request, book_id):
    """Books in the same category."""
    # Get book category
    try:
        r = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/", timeout=3)
        if r.status_code != 200:
            return Response({'error': 'Book not found'}, status=404)
        book = r.json()
        category_id = book.get('category_id')
    except Exception:
        return Response({'error': 'Book service unavailable'}, status=503)

    # Get books in same category, excluding this book
    try:
        r = requests.get(
            f"{settings.BOOK_SERVICE_URL}/api/books/?category_id={category_id}",
            timeout=3
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                data = data.get('results', [])
            similar = [b for b in data if b.get('book_id') != int(book_id)]
            return Response({'book_id': book_id, 'similar': similar[:10]})
    except Exception:
        pass
    return Response({'book_id': book_id, 'similar': []})
