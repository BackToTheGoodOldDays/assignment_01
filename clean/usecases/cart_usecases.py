"""
Cart Use Cases - Application Layer
Contains application-specific business logic for cart operations.
"""
from typing import Optional
from decimal import Decimal
from domain.entities.cart import Cart, CartItem
from domain.entities.book import Book
from interfaces.repositories.cart_repository import CartRepositoryInterface
from interfaces.repositories.book_repository import BookRepositoryInterface


class GetOrCreateCartUseCase:
    """Use case for getting or creating a customer's active cart."""
    
    def __init__(self, cart_repository: CartRepositoryInterface):
        self.cart_repository = cart_repository
    
    def execute(self, customer_id: int) -> Cart:
        """
        Get the active cart for a customer, or create one if it doesn't exist.
        
        Args:
            customer_id: The customer's ID
            
        Returns:
            Cart entity
        """
        cart = self.cart_repository.find_active_by_customer_id(customer_id)
        if not cart:
            cart = Cart(customer_id=customer_id, is_active=True)
            cart = self.cart_repository.save(cart)
        return cart


class AddToCartUseCase:
    """Use case for adding a book to the cart."""
    
    def __init__(self, cart_repository: CartRepositoryInterface,
                 book_repository: BookRepositoryInterface):
        self.cart_repository = cart_repository
        self.book_repository = book_repository
    
    def execute(self, customer_id: int, book_id: int, quantity: int = 1) -> Cart:
        """
        Add a book to the customer's cart.
        
        Args:
            customer_id: The customer's ID
            book_id: The book's ID to add
            quantity: Quantity to add (default: 1)
            
        Returns:
            Updated Cart entity
            
        Raises:
            ValueError: If book not found or insufficient stock
        """
        # Get the book
        book = self.book_repository.find_by_id(book_id)
        if not book:
            raise ValueError(f"Book with ID {book_id} not found")
        
        if not book.is_available:
            raise ValueError(f"'{book.title}' is out of stock")
        
        if quantity > book.stock:
            raise ValueError(f"Only {book.stock} copies available")
        
        # Get or create cart
        cart = self.cart_repository.find_active_by_customer_id(customer_id)
        if not cart:
            cart = Cart(customer_id=customer_id, is_active=True)
        
        # Create cart item
        cart_item = CartItem(
            book_id=book_id,
            book_title=book.title,
            book_author=book.author,
            book_price=book.price,
            quantity=quantity
        )
        
        # Add to cart
        cart.add_item(cart_item)
        
        # Save and return
        return self.cart_repository.save(cart)


class UpdateCartItemUseCase:
    """Use case for updating cart item quantity."""
    
    def __init__(self, cart_repository: CartRepositoryInterface,
                 book_repository: BookRepositoryInterface):
        self.cart_repository = cart_repository
        self.book_repository = book_repository
    
    def execute(self, customer_id: int, book_id: int, quantity: int) -> Cart:
        """
        Update the quantity of a book in the cart.
        
        Args:
            customer_id: The customer's ID
            book_id: The book's ID to update
            quantity: New quantity (0 to remove)
            
        Returns:
            Updated Cart entity
        """
        cart = self.cart_repository.find_active_by_customer_id(customer_id)
        if not cart:
            raise ValueError("Cart not found")
        
        if quantity <= 0:
            cart.remove_item(book_id)
        else:
            # Check stock
            book = self.book_repository.find_by_id(book_id)
            if book and quantity > book.stock:
                quantity = book.stock
            
            cart.update_item_quantity(book_id, quantity)
        
        return self.cart_repository.save(cart)


class RemoveFromCartUseCase:
    """Use case for removing a book from the cart."""
    
    def __init__(self, cart_repository: CartRepositoryInterface):
        self.cart_repository = cart_repository
    
    def execute(self, customer_id: int, book_id: int) -> Cart:
        """
        Remove a book from the customer's cart.
        
        Args:
            customer_id: The customer's ID
            book_id: The book's ID to remove
            
        Returns:
            Updated Cart entity
        """
        cart = self.cart_repository.find_active_by_customer_id(customer_id)
        if not cart:
            raise ValueError("Cart not found")
        
        cart.remove_item(book_id)
        return self.cart_repository.save(cart)


class ClearCartUseCase:
    """Use case for clearing all items from the cart."""
    
    def __init__(self, cart_repository: CartRepositoryInterface):
        self.cart_repository = cart_repository
    
    def execute(self, customer_id: int) -> Cart:
        """
        Clear all items from the customer's cart.
        
        Args:
            customer_id: The customer's ID
            
        Returns:
            Updated (empty) Cart entity
        """
        cart = self.cart_repository.find_active_by_customer_id(customer_id)
        if not cart:
            raise ValueError("Cart not found")
        
        cart.clear()
        return self.cart_repository.save(cart)


class GetCartUseCase:
    """Use case for retrieving the customer's cart."""
    
    def __init__(self, cart_repository: CartRepositoryInterface):
        self.cart_repository = cart_repository
    
    def execute(self, customer_id: int) -> Optional[Cart]:
        """
        Get the customer's active cart.
        
        Args:
            customer_id: The customer's ID
            
        Returns:
            Cart entity if found, None otherwise
        """
        return self.cart_repository.find_active_by_customer_id(customer_id)
