"""
Django models for Clean Architecture bookstore.
These are the persistence layer models that map to database tables.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomerModelManager(BaseUserManager):
    """Custom manager for CustomerModel."""
    
    def create_user(self, email, name, password=None, **extra_fields):
        """Create and return a regular customer."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        customer = self.model(email=email, name=name, **extra_fields)
        customer.set_password(password)
        customer.save(using=self._db)
        return customer
    
    def create_superuser(self, email, name, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, name, password, **extra_fields)


class CustomerModel(AbstractBaseUser, PermissionsMixin):
    """Django model for Customer persistence."""
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomerModelManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class BookModel(models.Model):
    """Django model for Book persistence."""
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        return self.stock > 0


class CartModel(models.Model):
    """Django model for Cart persistence."""
    
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        CustomerModel,
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
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItemModel(models.Model):
    """Django model for CartItem persistence."""
    
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(
        CartModel,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book = models.ForeignKey(
        BookModel,
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
        return self.quantity * self.book.price
