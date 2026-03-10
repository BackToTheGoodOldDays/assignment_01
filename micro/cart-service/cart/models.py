from django.db import models
from decimal import Decimal


class CartStatus(models.Model):
    """Model representing cart status (e.g., active, checked_out, abandoned)"""
    status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cart_statuses'
        verbose_name = 'Cart Status'
        verbose_name_plural = 'Cart Statuses'

    def __str__(self):
        return self.name


class Cart(models.Model):
    """Model representing a shopping cart"""
    cart_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField(db_index=True)  # Reference to customer-service
    status = models.ForeignKey(
        CartStatus,
        on_delete=models.PROTECT,
        related_name='carts'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Cart {self.cart_id} - Customer {self.customer_id}"

    @property
    def total_items(self):
        """Returns the total number of items in the cart"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Returns the total price of all items in the cart"""
        return self.calculate_total()

    def calculate_total(self):
        """Calculate the total price of all items in the cart"""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.subtotal
        return total


class CartItem(models.Model):
    """Model representing an item in a shopping cart"""
    item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book_id = models.IntegerField(db_index=True)  # Reference to book-service
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'book_id']
        ordering = ['-added_at']

    def __str__(self):
        return f"CartItem {self.item_id} - Book {self.book_id} x {self.quantity}"

    @property
    def subtotal(self):
        """Returns the subtotal for this cart item"""
        return Decimal(str(self.unit_price)) * Decimal(str(self.quantity))


class SavedCart(models.Model):
    """Model representing a saved/wishlisted cart"""
    saved_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField(db_index=True)  # Reference to customer-service
    original_cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='saved_versions'
    )
    cart_data = models.JSONField()  # Stores cart items as JSON
    name = models.CharField(max_length=255, blank=True, default='Saved Cart')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_carts'
        verbose_name = 'Saved Cart'
        verbose_name_plural = 'Saved Carts'
        ordering = ['-created_at']

    def __str__(self):
        return f"SavedCart {self.saved_id} - {self.name} (Customer {self.customer_id})"
