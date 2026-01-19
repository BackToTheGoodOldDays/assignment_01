from django.db import models
from django.conf import settings
from books.models import Book


class Cart(models.Model):
    """Shopping cart model."""
    
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cart #{self.id} - {self.customer.name}"
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.subtotal for item in self.items.all())
    
    @classmethod
    def get_or_create_active_cart(cls, customer):
        """Get or create an active cart for the customer."""
        cart, created = cls.objects.get_or_create(
            customer=customer,
            is_active=True,
            defaults={'customer': customer}
        )
        return cart


class CartItem(models.Model):
    """Cart item model representing a book in the cart."""
    
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'book')
    
    def __str__(self):
        return f"{self.quantity}x {self.book.title}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item."""
        return self.quantity * self.book.price
