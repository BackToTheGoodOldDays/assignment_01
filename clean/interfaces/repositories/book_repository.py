"""
Book Repository Interface - Interfaces Layer
Defines the contract for book data access.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.book import Book


class BookRepositoryInterface(ABC):
    """Abstract interface for book repository operations."""
    
    @abstractmethod
    def save(self, book: Book) -> Book:
        """Save a book entity."""
        pass
    
    @abstractmethod
    def find_by_id(self, book_id: int) -> Optional[Book]:
        """Find a book by ID."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Book]:
        """Get all books."""
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Book]:
        """Search books by title or author."""
        pass
    
    @abstractmethod
    def delete(self, book_id: int) -> bool:
        """Delete a book by ID."""
        pass
