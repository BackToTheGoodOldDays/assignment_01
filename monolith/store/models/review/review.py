"""
Review domain models: Rating, Review, UserBehavior, PurchaseHistory, Recommendation.
"""
from django.db import models
from django.conf import settings
from django.db.models import Avg, Count


class Rating(models.Model):
    """
    Rating model for book ratings by customers.
    Attributes: ratingId, score
    Methods: submitRating()
    """
    rating_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    book = models.ForeignKey('store.Book', on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_rating'
        verbose_name = 'Rating'
        unique_together = ['customer', 'book']

    def __str__(self):
        return f"Rating {self.score}/5 by {self.customer}"

    def submit_rating(self):
        self.save()


class Review(models.Model):
    """
    Review model for book reviews by customers.
    Attributes: reviewId, content
    Methods: writeReview()
    """
    review_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey('store.Book', on_delete=models.CASCADE, related_name='reviews')
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_review'
        verbose_name = 'Review'

    def __str__(self):
        return f"Review by {self.customer} on {self.book}"

    def write_review(self):
        self.save()


class UserBehavior(models.Model):
    """
    User behavior model for tracking customer actions.
    Attributes: behaviorId, action
    Methods: analyze()
    """
    BEHAVIOR_TYPES = [
        ('view', 'View'),
        ('search', 'Search'),
        ('add_to_cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
        ('wishlist', 'Wishlist'),
    ]

    behavior_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='behaviors')
    book = models.ForeignKey('store.Book', on_delete=models.CASCADE, related_name='user_behaviors')
    action = models.CharField(max_length=50, choices=BEHAVIOR_TYPES)
    search_query = models.CharField(max_length=255, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_userbehavior'
        verbose_name = 'User Behavior'

    def __str__(self):
        return f"{self.customer} - {self.action} - {self.book}"

    @classmethod
    def analyze(cls, customer):
        return cls.objects.filter(customer=customer).values('action').annotate(count=Count('action'))

    @classmethod
    def _get_category_preferences(cls, customer):
        return cls.objects.filter(
            customer=customer, action='view'
        ).values('book__category').annotate(count=Count('book__category')).order_by('-count')


class PurchaseHistory(models.Model):
    """
    Purchase history model for tracking customer purchases.
    Attributes: historyId, date
    Methods: getHistory()
    """
    history_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_histories')
    book = models.ForeignKey('store.Book', on_delete=models.CASCADE)
    order = models.ForeignKey('store.Order', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_purchasehistory'
        verbose_name = 'Purchase History'

    def __str__(self):
        return f"{self.customer} purchased {self.book}"

    @classmethod
    def get_history(cls, customer):
        return cls.objects.filter(customer=customer).order_by('-purchase_date')


class RecommendationRule(models.Model):
    """
    Recommendation rule model for defining recommendation logic.
    Attributes: ruleId, description
    Methods: applyRule()
    """
    RULE_TYPES = [
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content Based'),
        ('popularity', 'Popularity Based'),
        ('trending', 'Trending'),
    ]

    rule_id = models.AutoField(primary_key=True)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    description = models.TextField(blank=True, null=True)
    priority = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    min_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_results = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_recommendationrule'
        verbose_name = 'Recommendation Rule'

    def __str__(self):
        return f"{self.rule_type} Rule"

    def apply_rule(self, customer, current_book=None):
        return []


class Recommendation(models.Model):
    """
    Recommendation model for storing generated recommendations.
    Attributes: recommendId, date
    Methods: generate()
    """
    recommend_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    book = models.ForeignKey('store.Book', on_delete=models.CASCADE)
    rule = models.ForeignKey(RecommendationRule, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    reason = models.CharField(max_length=255, blank=True, null=True)
    is_shown = models.BooleanField(default=False)
    is_clicked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_recommendation'
        verbose_name = 'Recommendation'
        ordering = ['-score']

    def __str__(self):
        return f"Recommend {self.book} for {self.customer}"

    @classmethod
    def generate(cls, customer, limit=10):
        from store.models.book.book import Book
        books = Book.objects.exclude(
            ratings__customer=customer
        ).order_by('-created_at')[:limit]
        recommendations = []
        for book in books:
            rec, _ = cls.objects.get_or_create(
                customer=customer, book=book,
                defaults={'score': 0.5, 'reason': 'New arrival'}
            )
            recommendations.append(rec)
        return recommendations
