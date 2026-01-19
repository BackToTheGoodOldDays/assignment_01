from django.db import models


class Cart(models.Model):
    """Cart model for the microservice."""
    
    id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField()  # Reference to customer in customer-service
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'carts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cart #{self.id} - Customer {self.customer_id}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """CartItem model for the microservice."""
    
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()  # Reference to book in book-service
    book_title = models.CharField(max_length=255)  # Cached for display
    book_author = models.CharField(max_length=255)  # Cached for display
    book_price = models.DecimalField(max_digits=10, decimal_places=2)  # Cached price
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'book_id')
    
    def __str__(self):
        return f"{self.quantity}x {self.book_title}"
    
    @property
    def subtotal(self):
        return self.quantity * self.book_price
