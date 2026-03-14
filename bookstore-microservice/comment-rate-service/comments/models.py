from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    book_id = models.IntegerField(db_index=True)
    customer_id = models.IntegerField(db_index=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ('book_id', 'customer_id')

    def __str__(self):
        return f"Review by customer {self.customer_id} for book {self.book_id}"
