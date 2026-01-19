from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomerManager(BaseUserManager):
    """Custom manager for Customer model."""
    
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
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, name, password, **extra_fields)


class Customer(AbstractBaseUser, PermissionsMixin):
    """Custom Customer model for the bookstore."""
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomerManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return f"{self.name} ({self.email})"
