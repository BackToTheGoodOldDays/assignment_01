"""
Book controller - handles book catalog, detail, categories, authors.
"""
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from store.models.book.book import Book, Category, Author, Publisher, BookInventory
from store.models.review.review import Recommendation


class BookCatalogView(View):
    """Display book catalog with filtering and pagination."""

    def get(self, request):
        books = Book.objects.select_related('author', 'category', 'publisher', 'status').prefetch_related('images', 'book_rating').all()

        # Search
        search = request.GET.get('search', '').strip()
        if search:
            books = books.filter(
                Q(title__icontains=search) | Q(author__name__icontains=search) | Q(isbn__icontains=search)
            )

        # Category filter
        category_id = request.GET.get('category')
        if category_id:
            books = books.filter(category_id=category_id)

        # Author filter
        author_id = request.GET.get('author')
        if author_id:
            books = books.filter(author_id=author_id)

        # Price filter
        price_min = request.GET.get('price_min')
        price_max = request.GET.get('price_max')
        if price_min:
            books = books.filter(price__gte=price_min)
        if price_max:
            books = books.filter(price__lte=price_max)

        # Sort
        sort = request.GET.get('sort', '-created_at')
        sort_options = {
            'price_asc': 'price',
            'price_desc': '-price',
            'newest': '-created_at',
            'title': 'title',
            'popular': '-book_rating__total_ratings',
        }
        books = books.order_by(sort_options.get(sort, '-created_at'))

        # Pagination
        paginator = Paginator(books, 12)
        page = request.GET.get('page')
        books = paginator.get_page(page)

        categories = Category.objects.annotate(book_count=Count('books')).all()
        authors = Author.objects.annotate(book_count=Count('books')).all()

        return render(request, 'books/catalog.html', {
            'books': books,
            'categories': categories,
            'authors': authors,
            'is_paginated': books.has_other_pages(),
            'page_obj': books,
        })


class BookDetailView(View):
    """Display book detail page."""

    def get(self, request, book_id):
        book = get_object_or_404(
            Book.objects.select_related(
                'author', 'category', 'publisher', 'status', 'description', 'book_rating', 'inventory'
            ).prefetch_related('images', 'reviews__customer', 'reviews__rating'),
            book_id=book_id
        )

        # Related books (same category)
        related_books = Book.objects.filter(
            category=book.category
        ).exclude(book_id=book.book_id).prefetch_related('images')[:6]

        # Recommendations
        recommendations = []
        if request.user.is_authenticated:
            recs = Recommendation.objects.filter(
                customer=request.user
            ).select_related('book').prefetch_related('book__images')[:6]
            recommendations = [r.book for r in recs]

        return render(request, 'books/detail.html', {
            'book': book,
            'related_books': related_books,
            'recommendations': recommendations,
        })


class CategoryListView(View):
    """Display all categories."""

    def get(self, request):
        categories = Category.objects.annotate(book_count=Count('books')).all()
        return render(request, 'books/categories.html', {'categories': categories})


class CategoryDetailView(View):
    """Display books in a category."""

    def get(self, request, category_id):
        category = get_object_or_404(Category, category_id=category_id)
        books = Book.objects.filter(category=category).select_related('author').prefetch_related('images')

        q = request.GET.get('q', '').strip()
        if q:
            books = books.filter(Q(title__icontains=q) | Q(author__name__icontains=q))

        sort = request.GET.get('sort', '-created_at')
        sort_options = {'price_asc': 'price', 'price_desc': '-price', 'newest': '-created_at', 'title': 'title'}
        books = books.order_by(sort_options.get(sort, '-created_at'))

        paginator = Paginator(books, 12)
        page = request.GET.get('page')
        books = paginator.get_page(page)

        return render(request, 'books/category_detail.html', {
            'category': category,
            'books': books,
            'is_paginated': books.has_other_pages(),
            'page_obj': books,
        })


class AuthorListView(View):
    """Display all authors."""

    def get(self, request):
        authors = Author.objects.annotate(book_count=Count('books')).all()
        q = request.GET.get('q', '').strip()
        if q:
            authors = authors.filter(name__icontains=q)

        paginator = Paginator(authors, 20)
        page = request.GET.get('page')
        authors = paginator.get_page(page)

        return render(request, 'books/authors.html', {
            'authors': authors,
            'is_paginated': authors.has_other_pages(),
            'page_obj': authors,
        })


class AuthorDetailView(View):
    """Display author detail with their books."""

    def get(self, request, author_id):
        author = get_object_or_404(Author, author_id=author_id)
        books = Book.objects.filter(author=author).select_related('category').prefetch_related('images')

        paginator = Paginator(books, 12)
        page = request.GET.get('page')
        books = paginator.get_page(page)

        return render(request, 'books/author_detail.html', {
            'author': author,
            'books': books,
            'is_paginated': books.has_other_pages(),
            'page_obj': books,
        })


def get_recommendations(request):
    """Get recommendations for the current user."""
    if not request.user.is_authenticated:
        return []
    recs = Recommendation.objects.filter(customer=request.user).select_related('book')[:10]
    return [r.book for r in recs]


def get_recommendations_for_book(request, book_id):
    """Get recommendations based on a specific book."""
    book = get_object_or_404(Book, book_id=book_id)
    return Book.objects.filter(category=book.category).exclude(book_id=book_id)[:6]


def get_related_books(book):
    """Get related books for a given book."""
    return Book.objects.filter(category=book.category).exclude(book_id=book.book_id)[:6]


# API views
def book_list_api(request):
    """API: List books."""
    books = Book.objects.all()[:20]
    data = [{'id': b.book_id, 'title': b.title, 'price': str(b.price)} for b in books]
    return JsonResponse({'books': data})


def recommendations_api(request):
    """API: Get recommendations."""
    if not request.user.is_authenticated:
        return JsonResponse({'recommendations': []})
    recs = Recommendation.objects.filter(customer=request.user).select_related('book')[:10]
    data = [{'id': r.book.book_id, 'title': r.book.title, 'score': str(r.score)} for r in recs]
    return JsonResponse({'recommendations': data})


def categories_api(request):
    """API: List categories."""
    cats = Category.objects.annotate(book_count=Count('books')).all()
    data = [{'id': c.category_id, 'name': c.name, 'book_count': c.book_count} for c in cats]
    return JsonResponse({'categories': data})


def authors_api(request):
    """API: List authors."""
    auths = Author.objects.annotate(book_count=Count('books')).all()
    data = [{'id': a.author_id, 'name': a.name, 'book_count': a.book_count} for a in auths]
    return JsonResponse({'authors': data})
