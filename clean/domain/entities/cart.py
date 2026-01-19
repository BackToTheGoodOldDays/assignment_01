"""
Cart Entity - Domain Layer
Represents the Cart and CartItem business entities independent of any framework.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


@dataclass
class CartItem:
    """CartItem entity representing a book in the cart."""
    
    id: Optional[int] = None
    cart_id: Optional[int] = None
    book_id: int = 0
    book_title: str = ""
    book_author: str = ""
    book_price: Decimal = Decimal("0.00")
    quantity: int = 1
    added_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.added_at is None:
            self.added_at = datetime.now()
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal for this cart item."""
        return self.book_price * self.quantity
    
    def update_quantity(self, quantity: int) -> None:
        """Update item quantity."""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        self.quantity = quantity
    
    def __str__(self):
        return f"CartItem({self.quantity}x {self.book_title})"


@dataclass
class Cart:
    """Cart entity representing a shopping cart."""
    
    id: Optional[int] = None
    customer_id: int = 0
    items: List[CartItem] = field(default_factory=list)
    created_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def total_items(self) -> int:
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price of all items in cart."""
        return sum(item.subtotal for item in self.items)
    
    def add_item(self, item: CartItem) -> None:
        """Add an item to the cart."""
        # Check if item already exists
        for existing_item in self.items:
            if existing_item.book_id == item.book_id:
                existing_item.quantity += item.quantity
                return
        self.items.append(item)
    
    def remove_item(self, book_id: int) -> None:
        """Remove an item from the cart by book ID."""
        self.items = [item for item in self.items if item.book_id != book_id]
    
    def update_item_quantity(self, book_id: int, quantity: int) -> None:
        """Update quantity of an item in the cart."""
        for item in self.items:
            if item.book_id == book_id:
                item.update_quantity(quantity)
                return
        raise ValueError(f"Item with book_id {book_id} not found in cart")
    
    def clear(self) -> None:
        """Clear all items from the cart."""
        self.items = []
    
    def __str__(self):
        return f"Cart({self.id}, {self.total_items} items)"
