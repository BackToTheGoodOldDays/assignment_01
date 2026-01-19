"""
Book Entity - Domain Layer
Represents the Book business entity independent of any framework.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Book:
    """Book entity representing a book in the bookstore catalog."""
    
    id: Optional[int] = None
    title: str = ""
    author: str = ""
    price: Decimal = Decimal("0.00")
    stock: int = 0
    description: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate book data."""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Book title is required")
        if not self.author or len(self.author.strip()) == 0:
            raise ValueError("Book author is required")
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")
        return True
    
    @property
    def is_available(self) -> bool:
        """Check if book is available in stock."""
        return self.stock > 0
    
    def decrease_stock(self, quantity: int) -> None:
        """Decrease stock by given quantity."""
        if quantity > self.stock:
            raise ValueError(f"Insufficient stock. Available: {self.stock}")
        self.stock -= quantity
    
    def increase_stock(self, quantity: int) -> None:
        """Increase stock by given quantity."""
        self.stock += quantity
    
    def __str__(self):
        return f"Book({self.title} by {self.author})"
