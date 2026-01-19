"""
Django Book Repository - Infrastructure Layer
Implementation of BookRepositoryInterface using Django ORM.
"""
from typing import Optional, List
from decimal import Decimal
from django.db.models import Q
from domain.entities.book import Book
from interfaces.repositories.book_repository import BookRepositoryInterface
from framework.models import BookModel


class DjangoBookRepository(BookRepositoryInterface):
    """Django ORM implementation of book repository."""
    
    def save(self, book: Book) -> Book:
        """Save a book entity."""
        if book.id:
            # Update existing
            book_model = BookModel.objects.get(id=book.id)
            book_model.title = book.title
            book_model.author = book.author
            book_model.price = book.price
            book_model.stock = book.stock
            book_model.description = book.description
            book_model.save()
        else:
            # Create new
            book_model = BookModel.objects.create(
                title=book.title,
                author=book.author,
                price=book.price,
                stock=book.stock,
                description=book.description
            )
        
        return self._to_entity(book_model)
    
    def find_by_id(self, book_id: int) -> Optional[Book]:
        """Find a book by ID."""
        try:
            book_model = BookModel.objects.get(id=book_id)
            return self._to_entity(book_model)
        except BookModel.DoesNotExist:
            return None
    
    def find_all(self) -> List[Book]:
        """Get all books."""
        return [self._to_entity(b) for b in BookModel.objects.all().order_by('title')]
    
    def search(self, query: str) -> List[Book]:
        """Search books by title or author."""
        books = BookModel.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        ).order_by('title')
        return [self._to_entity(b) for b in books]
    
    def delete(self, book_id: int) -> bool:
        """Delete a book by ID."""
        try:
            BookModel.objects.filter(id=book_id).delete()
            return True
        except:
            return False
    
    def _to_entity(self, model: BookModel) -> Book:
        """Convert Django model to domain entity."""
        return Book(
            id=model.id,
            title=model.title,
            author=model.author,
            price=Decimal(str(model.price)),
            stock=model.stock,
            description=model.description
        )
