from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class BookStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'book_statuses'

    def __str__(self):
        return self.status_name


class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    author_id = models.IntegerField(db_index=True)
    category_id = models.IntegerField(db_index=True)
    publisher_id = models.IntegerField(db_index=True)
    status = models.ForeignKey(BookStatus, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.CharField(max_length=50, default='English')
    pages = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)
    publication_year = models.IntegerField(null=True, blank=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'books'

    def __str__(self):
        return self.title


class BookInventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField(default=0)
    min_stock = models.IntegerField(default=5)
    last_restocked = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'book_inventories'
