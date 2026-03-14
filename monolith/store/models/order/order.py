"""
Order domain models: Order, OrderItem, Payment, Shipping, etc.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid


class OrderStatus(models.Model):
    """
    Order status model for tracking order state.
    Attributes: statusId, name
    Methods: updateStatus()
    """
    status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, default='gray')
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'store_orderstatus'
        verbose_name = 'Order Status'
        ordering = ['sort_order']

    def __str__(self):
        return self.name

    def update_status(self, order, new_status):
        order.status = new_status
        order.save()


class PaymentMethod(models.Model):
    """
    Payment method model for available payment options.
    Attributes: methodId, name
    Methods: selectMethod()
    """
    method_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    processing_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('99999999.99'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_paymentmethod'
        verbose_name = 'Payment Method'

    def __str__(self):
        return self.name

    def select_method(self, amount):
        if self.min_amount <= amount <= self.max_amount:
            return True
        return False


class PaymentStatus(models.Model):
    """
    Payment status model for tracking payment state.
    Attributes: statusId, name
    Methods: updateStatus()
    """
    status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_paymentstatus'
        verbose_name = 'Payment Status'

    def __str__(self):
        return self.name

    def update_status(self, payment, new_status):
        payment.status = new_status
        payment.save()


class Payment(models.Model):
    """
    Payment model for order payments.
    Attributes: paymentId, amount, status
    Methods: processPayment()
    """
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='payments')
    method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    status = models.ForeignKey(PaymentStatus, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_payment'
        verbose_name = 'Payment'

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount}"

    def process_payment(self):
        self.payment_date = timezone.now()
        self.transaction_id = str(uuid.uuid4())[:20]
        completed = PaymentStatus.objects.filter(name='Completed').first()
        if completed:
            self.status = completed
        self.save()


class Transaction(models.Model):
    """
    Transaction model for recording payment transactions.
    Attributes: transactionId, time
    Methods: recordTransaction()
    """
    TRANSACTION_TYPES = [
        ('charge', 'Charge'),
        ('refund', 'Refund'),
        ('void', 'Void'),
    ]

    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='VND')
    transaction_time = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)

    class Meta:
        db_table = 'store_transaction'
        verbose_name = 'Transaction'

    def __str__(self):
        return f"Transaction {self.transaction_id}"

    @classmethod
    def record_transaction(cls, payment, transaction_type, amount, details=None):
        return cls.objects.create(
            payment=payment,
            transaction_type=transaction_type,
            amount=amount,
            details=details or {},
        )


class PaymentReceipt(models.Model):
    """
    Payment receipt model for generating receipts.
    Attributes: receiptId, date
    Methods: generateReceipt()
    """
    receipt_id = models.AutoField(primary_key=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_date = models.DateTimeField(auto_now_add=True)
    pdf_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'store_paymentreceipt'
        verbose_name = 'Payment Receipt'

    def __str__(self):
        return f"Receipt {self.receipt_number}"

    def generate_receipt(self):
        self.receipt_number = f"RCP-{self.payment.payment_id}-{uuid.uuid4().hex[:8].upper()}"
        self.save()


class Refund(models.Model):
    """
    Refund model for processing refunds.
    Attributes: refundId, amount
    Methods: processRefund()
    """
    REFUND_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ]

    refund_id = models.AutoField(primary_key=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=REFUND_STATUS, default='pending')
    refund_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'store_refund'
        verbose_name = 'Refund'

    def __str__(self):
        return f"Refund {self.refund_id} - {self.amount}"

    def process_refund(self):
        self.status = 'processed'
        self.processed_at = timezone.now()
        self.refund_transaction_id = str(uuid.uuid4())[:20]
        self.save()


class ShippingMethod(models.Model):
    """
    Shipping method model for delivery options.
    Attributes: methodId, name
    Methods: selectMethod()
    """
    method_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    base_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    per_kg_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estimated_days_min = models.PositiveIntegerField(default=1)
    estimated_days_max = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_shippingmethod'
        verbose_name = 'Shipping Method'

    def __str__(self):
        return self.name

    def select_method(self):
        return self.is_active

    def calculate_fee(self, weight=0):
        return self.base_fee + (self.per_kg_fee * Decimal(str(weight)))


class ShippingStatus(models.Model):
    """
    Shipping status model for tracking shipment state.
    Attributes: statusId, name
    Methods: updateStatus()
    """
    status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'store_shippingstatus'
        verbose_name = 'Shipping Status'
        ordering = ['sort_order']

    def __str__(self):
        return self.name

    def update_status(self, shipment, new_status):
        shipment.status = new_status
        shipment.save()


class DeliveryAddress(models.Model):
    """
    Delivery address model for customer addresses.
    Attributes: addressId, detail
    Methods: validateAddress()
    """
    address_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_addresses')
    recipient_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    ward = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default='Vi\u1ec7t Nam')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_deliveryaddress'
        verbose_name = 'Delivery Address'

    def __str__(self):
        return f"{self.recipient_name} - {self.city}"

    @property
    def detail(self):
        parts = [self.address_line1, self.address_line2, self.ward, self.district, self.city]
        return ', '.join([p for p in parts if p])

    def validate_address(self):
        return bool(self.recipient_name and self.phone and self.city)


class Shipping(models.Model):
    """
    Shipping model for order shipping details.
    Attributes: shippingId, fee
    Methods: calculateFee()
    """
    shipping_id = models.AutoField(primary_key=True)
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='shipping')
    method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True, related_name='shippings')
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_shipping'
        verbose_name = 'Shipping'

    def __str__(self):
        return f"Shipping for Order {self.order.order_id}"

    def calculate_fee(self):
        if self.method:
            self.fee = self.method.calculate_fee(self.weight)
            self.save()
        return self.fee


class Shipment(models.Model):
    """
    Shipment model for tracking actual shipments.
    Attributes: shipmentId, shipDate
    Methods: createShipment()
    """
    shipment_id = models.AutoField(primary_key=True)
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE, related_name='shipments')
    status = models.ForeignKey(ShippingStatus, on_delete=models.SET_NULL, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    ship_date = models.DateTimeField(blank=True, null=True)
    estimated_delivery = models.DateTimeField(blank=True, null=True)
    actual_delivery = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_shipment'
        verbose_name = 'Shipment'

    def __str__(self):
        return f"Shipment {self.shipment_id}"

    @classmethod
    def create_shipment(cls, shipping, carrier=None):
        return cls.objects.create(
            shipping=shipping,
            carrier=carrier,
            tracking_number=f"TN-{uuid.uuid4().hex[:12].upper()}",
            ship_date=timezone.now(),
        )


class DeliveryTracking(models.Model):
    """
    Delivery tracking model for tracking shipment progress.
    Attributes: trackingId, status
    Methods: trackDelivery()
    """
    tracking_id = models.AutoField(primary_key=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_updates')
    status = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_deliverytracking'
        verbose_name = 'Delivery Tracking'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.status} - {self.location}"

    @classmethod
    def track_delivery(cls, shipment, status, location=None, description=None):
        return cls.objects.create(
            shipment=shipment, status=status,
            location=location, description=description,
        )


class Order(models.Model):
    """
    Order model for customer orders.
    Attributes: orderId, orderDate, total
    Methods: placeOrder()
    """
    order_id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    cart = models.ForeignKey('store.Cart', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_order'
        verbose_name = 'Order'
        ordering = ['-order_date']

    def __str__(self):
        return f"Order {self.order_number}"

    @property
    def id(self):
        return self.order_id

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    @classmethod
    def place_order(cls, customer, cart, shipping_method=None, payment_method=None, delivery_address=None):
        from store.models.order.cart import CartItem
        order = cls.objects.create(
            customer=customer,
            cart=cart,
            status=OrderStatus.objects.filter(name='Pending').first(),
            subtotal=cart.calculate_total(),
            total_price=cart.calculate_total(),
        )
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                unit_price=item.book.price,
                subtotal=item.subtotal,
            )
        cart.is_active = False
        cart.save()
        return order


class OrderItem(models.Model):
    """
    Order item model for items in an order.
    Attributes: orderItemId, quantity
    Methods: calculatePrice()
    """
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey('store.Book', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_orderitem'
        verbose_name = 'Order Item'

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    def calculate_price(self):
        self.subtotal = self.unit_price * self.quantity
        self.save()
        return self.subtotal


class OrderHistory(models.Model):
    """
    Order history model for tracking order changes.
    Attributes: historyId, time
    Methods: trackStatus()
    """
    history_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    old_status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    new_status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    action = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_history_actions')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_orderhistory'
        verbose_name = 'Order History'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on Order {self.order.order_id}"

    @classmethod
    def track_status(cls, order, action, old_status=None, new_status=None, notes=None, created_by=None):
        return cls.objects.create(
            order=order, action=action,
            old_status=old_status, new_status=new_status,
            notes=notes, created_by=created_by,
        )


class Invoice(models.Model):
    """
    Invoice model for order invoices.
    Attributes: invoiceId, amount
    Methods: generateInvoice()
    """
    invoice_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    pdf_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'store_invoice'
        verbose_name = 'Invoice'

    def __str__(self):
        return f"Invoice {self.invoice_number}"

    @classmethod
    def generate_invoice(cls, order):
        return cls.objects.create(
            order=order,
            invoice_number=f"INV-{order.order_number}",
            amount=order.subtotal,
            tax_amount=order.tax_amount,
            discount_amount=order.discount_amount,
            total_amount=order.total_price,
        )


class OrderNote(models.Model):
    """
    Order note model for adding notes to orders.
    Attributes: noteId, content
    Methods: addNote()
    """
    note_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_notes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_ordernote'
        verbose_name = 'Order Note'

    def __str__(self):
        return f"Note on Order {self.order.order_id}"

    @classmethod
    def add_note(cls, order, content, created_by=None, is_internal=False):
        return cls.objects.create(
            order=order, content=content,
            created_by=created_by, is_internal=is_internal,
        )


class OrderSummary(models.Model):
    """
    Order summary model for aggregate order statistics.
    Attributes: totalItem, totalPrice
    Methods: summarize()
    """
    summary_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='summary')
    total_items = models.PositiveIntegerField(default=0)
    total_quantity = models.PositiveIntegerField(default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_ordersummary'
        verbose_name = 'Order Summary'

    def __str__(self):
        return f"Summary for Order {self.order.order_id}"

    def summarize(self):
        items = self.order.items.all()
        self.total_items = items.count()
        self.total_quantity = sum(item.quantity for item in items)
        self.subtotal = self.order.subtotal
        self.total_price = self.order.total_price
        self.save()


class OrderTracking(models.Model):
    """
    Order tracking model for tracking order progress.
    Attributes: trackingId, location
    Methods: trackOrder()
    """
    tracking_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_ordertracking'
        verbose_name = 'Order Tracking'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.status} - {self.location}"

    @classmethod
    def track_order(cls, order, status, location=None, description=None):
        return cls.objects.create(
            order=order, status=status,
            location=location, description=description,
        )


class OrderCancellation(models.Model):
    """
    Order cancellation model for handling order cancellations.
    Attributes: cancelId, reason
    Methods: cancelOrder()
    """
    CANCELLATION_STATUS = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    cancel_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='cancellation')
    reason = models.TextField()
    status = models.CharField(max_length=50, choices=CANCELLATION_STATUS, default='requested')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='cancellation_requests')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancellation_approvals')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'store_ordercancellation'
        verbose_name = 'Order Cancellation'

    def __str__(self):
        return f"Cancellation for Order {self.order.order_id}"

    def cancel_order(self, approved_by=None):
        self.status = 'approved'
        self.approved_by = approved_by
        self.processed_at = timezone.now()
        self.save()
        cancelled_status = OrderStatus.objects.filter(name='Cancelled').first()
        if cancelled_status:
            self.order.status = cancelled_status
            self.order.save()
