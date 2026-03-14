from django.db import models


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField(db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart #{self.cart_id} (Customer {self.customer_id})"


class CartItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'book_id')

    def __str__(self):
        return f"CartItem book {self.book_id} x{self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
