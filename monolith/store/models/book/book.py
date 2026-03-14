"""
Book domain models: Author, Category, Publisher, Book, BookImage, etc.
"""
from django.db import models
from django.db.models import Avg
from django.conf import settings


class Author(models.Model):
    """
    Author model for book authors.
    Attributes: authorId, name
    Methods: getBooks()
    """
    author_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    photo_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_author'
        verbose_name = 'Author'

    def __str__(self):
        return self.name

    def get_books(self):
        return self.books.all()


class Category(models.Model):
    """
    Category model for book categorization.
    Attributes: categoryId, name
    Methods: getBooksByCategory()
    """
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    icon = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_books_by_category(self):
        return self.books.all()


class Publisher(models.Model):
    """
    Publisher model for book publishers.
    Attributes: publisherId, name
    Methods: publishBook()
    """
    publisher_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_publisher'
        verbose_name = 'Publisher'

    def __str__(self):
        return self.name

    def publish_book(self, book_data):
        return Book.objects.create(publisher=self, **book_data)


class BookStatus(models.Model):
    """
    Book status model for tracking book availability status.
    Attributes: statusId, statusName
    Methods: updateStatus()
    """
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_bookstatus'
        verbose_name = 'Book Status'
        verbose_name_plural = 'Book Statuses'

    def __str__(self):
        return self.status_name

    def update_status(self, book, new_status):
        book.status = new_status
        book.save()


class BookTag(models.Model):
    """
    Book tag model for classifying books.
    Attributes: tagId, name
    Methods: classifyBook()
    """
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_booktag'
        verbose_name = 'Book Tag'

    def __str__(self):
        return self.name

    def classify_book(self, book):
        book.tags.add(self)


class Book(models.Model):
    """
    Book model for the bookstore catalog.
    Attributes: bookId, title, price
    Methods: getDetail()
    """
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    status = models.ForeignKey(BookStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    tags = models.ManyToManyField(BookTag, related_name='books', blank=True)
    publication_date = models.DateField(blank=True, null=True)
    pages = models.PositiveIntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, default='Vietnamese')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_book'
        verbose_name = 'Book'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def id(self):
        return self.book_id

    @property
    def is_available(self):
        try:
            return self.inventory.quantity > 0
        except BookInventory.DoesNotExist:
            return False

    @property
    def stock(self):
        try:
            return self.inventory.quantity
        except BookInventory.DoesNotExist:
            return 0

    @property
    def average_rating(self):
        from store.models.review.review import Rating
        result = Rating.objects.filter(book=self).aggregate(avg=Avg('score'))
        return result['avg'] or 0

    def get_detail(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'isbn': self.isbn,
            'price': str(self.price),
            'author': str(self.author) if self.author else '',
            'category': str(self.category) if self.category else '',
            'publisher': str(self.publisher) if self.publisher else '',
            'status': str(self.status) if self.status else '',
        }

    def get_description(self):
        try:
            return self.description
        except BookDescription.DoesNotExist:
            return None


class BookImage(models.Model):
    """
    Book image model for storing book images.
    Attributes: imageId, url
    Methods: display()
    """
    image_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_bookimage'
        verbose_name = 'Book Image'
        ordering = ['display_order']

    def __str__(self):
        return f"Image for {self.book.title}"

    def display(self):
        return self.url


class BookDescription(models.Model):
    """
    Book description model for detailed book descriptions.
    Attributes: descId, content
    Methods: showDescription()
    """
    desc_id = models.AutoField(primary_key=True)
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='description')
    content = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_bookdescription'
        verbose_name = 'Book Description'

    def __str__(self):
        return f"Description for {self.book.title}"

    def show_description(self):
        return self.content


class BookRating(models.Model):
    """
    Book rating model for aggregate book ratings.
    Attributes: ratingId, avgScore
    Methods: calculateAvg()
    """
    rating_id = models.AutoField(primary_key=True)
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='book_rating')
    avg_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_bookrating'
        verbose_name = 'Book Rating'

    def __str__(self):
        return f"Rating for {self.book.title}: {self.avg_score}"

    def calculate_avg(self):
        from store.models.review.review import Rating
        result = Rating.objects.filter(book=self.book).aggregate(avg=Avg('score'))
        self.avg_score = result['avg'] or 0
        self.total_ratings = Rating.objects.filter(book=self.book).count()
        self.save()


class BookInventory(models.Model):
    """
    Book inventory model for tracking stock.
    Attributes: inventoryId, quantity
    Methods: checkStock()
    """
    inventory_id = models.AutoField(primary_key=True)
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=5)
    max_stock_level = models.PositiveIntegerField(default=100)
    reorder_point = models.PositiveIntegerField(default=10)
    last_restocked = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_bookinventory'
        verbose_name = 'Book Inventory'

    def __str__(self):
        return f"Inventory for {self.book.title}: {self.quantity}"

    def check_stock(self):
        if self.quantity <= 0:
            return 'out_of_stock'
        elif self.quantity <= self.min_stock_level:
            return 'low_stock'
        return 'in_stock'

    def add_stock(self, quantity):
        self.quantity += quantity
        self.save()
        return self.check_stock()

    def reduce_stock(self, quantity):
        if quantity > self.quantity:
            raise ValueError('Insufficient stock')
        self.quantity -= quantity
        self.save()
        return self.check_stock()
