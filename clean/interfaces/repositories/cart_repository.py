"""
Cart Repository Interface - Interfaces Layer
Defines the contract for cart data access.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.cart import Cart


class CartRepositoryInterface(ABC):
    """Abstract interface for cart repository operations."""
    
    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """Save a cart entity."""
        pass
    
    @abstractmethod
    def find_by_id(self, cart_id: int) -> Optional[Cart]:
        """Find a cart by ID."""
        pass
    
    @abstractmethod
    def find_active_by_customer_id(self, customer_id: int) -> Optional[Cart]:
        """Find the active cart for a customer."""
        pass
    
    @abstractmethod
    def find_all_by_customer_id(self, customer_id: int) -> List[Cart]:
        """Get all carts for a customer."""
        pass
    
    @abstractmethod
    def delete(self, cart_id: int) -> bool:
        """Delete a cart by ID."""
        pass
    
    @abstractmethod
    def clear_cart(self, cart_id: int) -> bool:
        """Clear all items from a cart."""
        pass
