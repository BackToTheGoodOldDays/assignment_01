"""
Customer model - main user model for the bookstore.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomerManager(BaseUserManager):
    """Custom manager for Customer model."""

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)


class Customer(AbstractBaseUser, PermissionsMixin):
    """
    Customer model for the bookstore.
    Attributes: customerId, name, phone
    Methods: placeOrder()
    """
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group', related_name='customer_set',
        related_query_name='customer', blank=True,
        help_text='The groups this customer belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='customer_set',
        related_query_name='customer', blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this customer.',
    )
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'store_customer'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name

    @property
    def id(self):
        return self.customer_id

    def place_order(self, cart):
        from store.models.order.order import Order
        return Order.place_order(customer=self, cart=cart)

    def get_purchase_history(self):
        from store.models.review.review import PurchaseHistory
        return PurchaseHistory.get_history(self)

    def get_active_cart(self):
        from store.models.order.cart import Cart
        return Cart.get_or_create_active_cart(self)
