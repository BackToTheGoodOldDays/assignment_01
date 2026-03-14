"""
Cart domain models: CartStatus, Cart, CartItem, CartSummary, SavedCart, CartHistory.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class CartStatus(models.Model):
    """
    Cart status model for tracking cart state.
    Attributes: statusId, name
    Methods: changeStatus()
    """
    status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_cartstatus'
        verbose_name = 'Cart Status'

    def __str__(self):
        return self.name

    def change_status(self, cart, new_status):
        cart.status = new_status
        cart.save()


class Cart(models.Model):
    """
    Shopping cart model.
    Attributes: cartId, isActive
    Methods: calculateTotal()
    """
    cart_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    status = models.ForeignKey(CartStatus, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_cart'
        verbose_name = 'Cart'

    def __str__(self):
        return f"Cart {self.cart_id} - {self.customer}"

    @property
    def id(self):
        return self.cart_id

    @property
    def total_items(self):
        return self.items.count()

    @property
    def total_price(self):
        return self.calculate_total()

    def calculate_total(self):
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.subtotal
        return total

    @classmethod
    def get_or_create_active_cart(cls, customer):
        cart, created = cls.objects.get_or_create(
            customer=customer, is_active=True,
            defaults={'status': CartStatus.objects.filter(name='Active').first()}
        )
        return cart

    def save_cart(self):
        self.is_active = False
        self.save()


class CartItem(models.Model):
    """
    Cart item model representing a book in the cart.
    Attributes: itemId, quantity
    Methods: updateQuantity()
    """
    item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey('store.Book', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_cartitem'
        verbose_name = 'Cart Item'
        unique_together = ['cart', 'book']

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    @property
    def id(self):
        return self.item_id

    @property
    def subtotal(self):
        return self.book.price * self.quantity

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity
        self.save()


class CartSummary(models.Model):
    """
    Cart summary model for storing cart totals.
    Attributes: totalItem, totalPrice
    Methods: summarize()
    """
    summary_id = models.AutoField(primary_key=True)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='summary')
    total_items = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_cartsummary'
        verbose_name = 'Cart Summary'

    def __str__(self):
        return f"Summary for Cart {self.cart.cart_id}"

    def summarize(self):
        self.total_items = self.cart.total_items
        self.total_price = self.cart.calculate_total()
        self.final_total = self.total_price - self.discount_amount + self.tax_amount
        self.save()


class SavedCart(models.Model):
    """
    Saved cart model for storing cart state for later.
    Attributes: savedCartId, date
    Methods: restore()
    """
    saved_cart_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_carts')
    original_cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='saved_versions')
    name = models.CharField(max_length=100)
    cart_data = models.JSONField(default=dict)
    saved_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_savedcart'
        verbose_name = 'Saved Cart'

    def __str__(self):
        return f"Saved: {self.name}"

    def restore(self):
        cart = Cart.get_or_create_active_cart(self.customer)
        cart.items.all().delete()
        for item_data in self.cart_data.get('items', []):
            CartItem.objects.create(
                cart=cart,
                book_id=item_data['book_id'],
                quantity=item_data['quantity'],
            )
        return cart


class CartHistory(models.Model):
    """
    Cart history model for tracking cart changes.
    Attributes: historyId, action
    Methods: trackChange()
    """
    ACTION_TYPES = [
        ('add', 'Add Item'),
        ('remove', 'Remove Item'),
        ('update', 'Update Quantity'),
        ('clear', 'Clear Cart'),
        ('save', 'Save Cart'),
        ('restore', 'Restore Cart'),
    ]

    history_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    item = models.ForeignKey(CartItem, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_carthistory'
        verbose_name = 'Cart History'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on Cart {self.cart.cart_id}"

    @classmethod
    def track_change(cls, cart, action, item=None, details=None):
        return cls.objects.create(cart=cart, action=action, item=item, details=details)
