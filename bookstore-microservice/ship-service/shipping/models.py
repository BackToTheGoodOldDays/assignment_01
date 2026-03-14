from django.db import models
import uuid


class ShippingMethod(models.Model):
    method_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_days = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'shipping_methods'

    def __str__(self):
        return self.name


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    ]
    shipment_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(db_index=True)
    tracking_number = models.CharField(max_length=100, unique=True)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    carrier = models.CharField(max_length=100, blank=True, null=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    expected_delivery = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipments'

    def __str__(self):
        return self.tracking_number

    @classmethod
    def generate_tracking_number(cls):
        return f"TRK{uuid.uuid4().hex[:10].upper()}"
