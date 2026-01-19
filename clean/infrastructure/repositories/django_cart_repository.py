"""
Django Cart Repository - Infrastructure Layer
Implementation of CartRepositoryInterface using Django ORM.
"""
from typing import Optional, List
from decimal import Decimal
from domain.entities.cart import Cart, CartItem
from interfaces.repositories.cart_repository import CartRepositoryInterface
from framework.models import CartModel, CartItemModel


class DjangoCartRepository(CartRepositoryInterface):
    """Django ORM implementation of cart repository."""
    
    def save(self, cart: Cart) -> Cart:
        """Save a cart entity."""
        if cart.id:
            # Update existing cart
            cart_model = CartModel.objects.get(id=cart.id)
            cart_model.is_active = cart.is_active
            cart_model.save()
            
            # Sync cart items
            existing_item_ids = []
            for item in cart.items:
                if item.id:
                    # Update existing item
                    item_model = CartItemModel.objects.get(id=item.id)
                    item_model.quantity = item.quantity
                    item_model.save()
                    existing_item_ids.append(item.id)
                else:
                    # Create new item
                    item_model = CartItemModel.objects.create(
                        cart=cart_model,
                        book_id=item.book_id,
                        quantity=item.quantity
                    )
                    existing_item_ids.append(item_model.id)
            
            # Remove items not in entity
            CartItemModel.objects.filter(cart=cart_model).exclude(id__in=existing_item_ids).delete()
        else:
            # Create new cart
            cart_model = CartModel.objects.create(
                customer_id=cart.customer_id,
                is_active=cart.is_active
            )
            
            # Create cart items
            for item in cart.items:
                CartItemModel.objects.create(
                    cart=cart_model,
                    book_id=item.book_id,
                    quantity=item.quantity
                )
        
        # Reload and return
        return self.find_by_id(cart_model.id)
    
    def find_by_id(self, cart_id: int) -> Optional[Cart]:
        """Find a cart by ID."""
        try:
            cart_model = CartModel.objects.get(id=cart_id)
            return self._to_entity(cart_model)
        except CartModel.DoesNotExist:
            return None
    
    def find_active_by_customer_id(self, customer_id: int) -> Optional[Cart]:
        """Find the active cart for a customer."""
        try:
            cart_model = CartModel.objects.get(customer_id=customer_id, is_active=True)
            return self._to_entity(cart_model)
        except CartModel.DoesNotExist:
            return None
    
    def find_all_by_customer_id(self, customer_id: int) -> List[Cart]:
        """Get all carts for a customer."""
        return [self._to_entity(c) for c in CartModel.objects.filter(customer_id=customer_id)]
    
    def delete(self, cart_id: int) -> bool:
        """Delete a cart by ID."""
        try:
            CartModel.objects.filter(id=cart_id).delete()
            return True
        except:
            return False
    
    def clear_cart(self, cart_id: int) -> bool:
        """Clear all items from a cart."""
        try:
            CartItemModel.objects.filter(cart_id=cart_id).delete()
            return True
        except:
            return False
    
    def _to_entity(self, model: CartModel) -> Cart:
        """Convert Django model to domain entity."""
        items = []
        for item_model in model.items.all().select_related('book'):
            items.append(CartItem(
                id=item_model.id,
                cart_id=model.id,
                book_id=item_model.book.id,
                book_title=item_model.book.title,
                book_author=item_model.book.author,
                book_price=Decimal(str(item_model.book.price)),
                quantity=item_model.quantity,
                added_at=item_model.added_at
            ))
        
        return Cart(
            id=model.id,
            customer_id=model.customer_id,
            items=items,
            created_at=model.created_at,
            is_active=model.is_active
        )
