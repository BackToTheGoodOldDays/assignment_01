"""
Book Use Cases - Application Layer
Contains application-specific business logic for book operations.
"""
from typing import List, Optional
from domain.entities.book import Book
from interfaces.repositories.book_repository import BookRepositoryInterface


class GetAllBooksUseCase:
    """Use case for retrieving all books."""
    
    def __init__(self, book_repository: BookRepositoryInterface):
        self.book_repository = book_repository
    
    def execute(self, search: Optional[str] = None) -> List[Book]:
        """
        Get all books, optionally filtered by search term.
        
        Args:
            search: Optional search term to filter books
            
        Returns:
            List of Book entities
        """
        if search:
            return self.book_repository.search(search)
        return self.book_repository.find_all()


class GetBookByIdUseCase:
    """Use case for retrieving a book by ID."""
    
    def __init__(self, book_repository: BookRepositoryInterface):
        self.book_repository = book_repository
    
    def execute(self, book_id: int) -> Optional[Book]:
        """
        Get a book by its ID.
        
        Args:
            book_id: The book's ID
            
        Returns:
            Book entity if found, None otherwise
        """
        return self.book_repository.find_by_id(book_id)


class CreateBookUseCase:
    """Use case for creating a new book."""
    
    def __init__(self, book_repository: BookRepositoryInterface):
        self.book_repository = book_repository
    
    def execute(self, title: str, author: str, price: float, stock: int = 0, 
                description: str = None) -> Book:
        """
        Create a new book.
        
        Args:
            title: Book title
            author: Book author
            price: Book price
            stock: Initial stock quantity
            description: Book description
            
        Returns:
            Created Book entity
        """
        from decimal import Decimal
        
        book = Book(
            title=title,
            author=author,
            price=Decimal(str(price)),
            stock=stock,
            description=description
        )
        book.validate()
        
        return self.book_repository.save(book)


class UpdateBookStockUseCase:
    """Use case for updating book stock."""
    
    def __init__(self, book_repository: BookRepositoryInterface):
        self.book_repository = book_repository
    
    def execute(self, book_id: int, quantity_change: int) -> Book:
        """
        Update book stock (increase or decrease).
        
        Args:
            book_id: The book's ID
            quantity_change: Positive to increase, negative to decrease
            
        Returns:
            Updated Book entity
            
        Raises:
            ValueError: If book not found or insufficient stock
        """
        book = self.book_repository.find_by_id(book_id)
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        
        if quantity_change > 0:
            book.increase_stock(quantity_change)
        else:
            book.decrease_stock(abs(quantity_change))
        
        return self.book_repository.save(book)
