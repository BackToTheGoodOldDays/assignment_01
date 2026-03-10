from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class BookStatus(models.Model):
    """Model representing book availability status."""
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'book_statuses'
        verbose_name = 'Book Status'
        verbose_name_plural = 'Book Statuses'

    def __str__(self):
        return self.status_name


class BookTag(models.Model):
    """Model representing tags for categorizing books."""
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'book_tags'
        verbose_name = 'Book Tag'
        verbose_name_plural = 'Book Tags'

    def __str__(self):
        return self.name


class Book(models.Model):
    """Main book model with references to external services."""
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    # References to external services (catalog-service)
    author_id = models.IntegerField(db_index=True)
    category_id = models.IntegerField(db_index=True)
    publisher_id = models.IntegerField(db_index=True)
    
    status = models.ForeignKey(
        BookStatus,
        on_delete=models.PROTECT,
        related_name='books'
    )
    publication_date = models.DateField(blank=True, null=True)
    pages = models.PositiveIntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, default='English')
    
    tags = models.ManyToManyField(BookTag, related_name='books', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'books'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['author_id']),
            models.Index(fields=['category_id']),
        ]

    def __str__(self):
        return f"{self.title} (ISBN: {self.isbn})"


class BookImage(models.Model):
    """Model for storing book images."""
    image_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='images'
    )
    url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'book_images'
        verbose_name = 'Book Image'
        verbose_name_plural = 'Book Images'
        ordering = ['display_order']

    def __str__(self):
        return f"Image for {self.book.title}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per book
        if self.is_primary:
            BookImage.objects.filter(book=self.book, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class BookDescription(models.Model):
    """Model for storing book descriptions."""
    desc_id = models.AutoField(primary_key=True)
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        related_name='description'
    )
    content = models.TextField()
    short_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'book_descriptions'
        verbose_name = 'Book Description'
        verbose_name_plural = 'Book Descriptions'

    def __str__(self):
        return f"Description for {self.book.title}"


class BookRating(models.Model):
    """Model for storing aggregated book ratings."""
    rating_id = models.AutoField(primary_key=True)
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        related_name='rating'
    )
    avg_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('5.00'))
        ]
    )
    total_ratings = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'book_ratings'
        verbose_name = 'Book Rating'
        verbose_name_plural = 'Book Ratings'

    def __str__(self):
        return f"Rating for {self.book.title}: {self.avg_score}/5"

    def update_rating(self, new_score):
        """Update the average rating with a new score."""
        total_score = self.avg_score * self.total_ratings
        self.total_ratings += 1
        self.avg_score = (total_score + Decimal(str(new_score))) / self.total_ratings
        self.save()


class BookInventory(models.Model):
    """Model for managing book inventory."""
    inventory_id = models.AutoField(primary_key=True)
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=5)
    max_stock_level = models.PositiveIntegerField(default=100)
    reorder_point = models.PositiveIntegerField(default=10)
    last_restocked = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'book_inventories'
        verbose_name = 'Book Inventory'
        verbose_name_plural = 'Book Inventories'

    def __str__(self):
        return f"Inventory for {self.book.title}: {self.quantity} units"

    def check_stock(self):
        """Check stock status and return information."""
        return {
            'book_id': self.book.book_id,
            'quantity': self.quantity,
            'in_stock': self.quantity > 0,
            'low_stock': self.quantity <= self.min_stock_level,
            'needs_reorder': self.quantity <= self.reorder_point,
            'min_stock_level': self.min_stock_level,
            'max_stock_level': self.max_stock_level,
            'reorder_point': self.reorder_point,
            'last_restocked': self.last_restocked
        }

    def add_stock(self, amount):
        """Add stock to inventory."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        new_quantity = self.quantity + amount
        if new_quantity > self.max_stock_level:
            raise ValueError(f"Cannot exceed max stock level of {self.max_stock_level}")
        
        self.quantity = new_quantity
        self.last_restocked = timezone.now()
        self.save()
        return self.check_stock()

    def reduce_stock(self, amount):
        """Reduce stock from inventory."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if amount > self.quantity:
            raise ValueError(f"Insufficient stock. Available: {self.quantity}")
        
        self.quantity -= amount
        self.save()
        return self.check_stock()
