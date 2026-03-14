from django.db import models

class UserInteraction(models.Model):
    TYPES = [('view', 'View'), ('purchase', 'Purchase'), ('review', 'Review')]
    interaction_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField(db_index=True)
    book_id = models.IntegerField(db_index=True)
    interaction_type = models.CharField(max_length=20, choices=TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_interactions'

    def __str__(self):
        return f"Customer {self.customer_id} {self.interaction_type} book {self.book_id}"
