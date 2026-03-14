"""Book URL configuration."""
from django.urls import path
from store.controllers.bookController.book_controller import (
    BookCatalogView, BookDetailView,
    CategoryListView, CategoryDetailView,
    AuthorListView, AuthorDetailView,
    book_list_api, recommendations_api,
    categories_api, authors_api,
)

app_name = 'books'

urlpatterns = [
    path('', BookCatalogView.as_view(), name='catalog'),
    path('<int:book_id>/', BookDetailView.as_view(), name='detail'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('categories/<int:category_id>/', CategoryDetailView.as_view(), name='category'),
    path('authors/', AuthorListView.as_view(), name='authors'),
    path('authors/<int:author_id>/', AuthorDetailView.as_view(), name='author'),
    path('api/books/', book_list_api, name='api_books'),
    path('api/recommendations/', recommendations_api, name='api_recommendations'),
    path('api/categories/', categories_api, name='api_categories'),
    path('api/authors/', authors_api, name='api_authors'),
]
