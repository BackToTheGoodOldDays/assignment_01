"""
Staff domain models: Staff, Admin, InventoryLog, AdminActionLog.
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class Staff(models.Model):
    """
    Staff model for store employees.
    Attributes: staffId, name, role
    Methods: manageInventory()
    """
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('sales', 'Sales'),
        ('warehouse', 'Warehouse'),
        ('support', 'Support'),
    ]

    staff_id = models.AutoField(primary_key=True)
    employee_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='sales')
    is_active = models.BooleanField(default=True)
    hire_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'store_staff'
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'

    def __str__(self):
        return f"{self.name} ({self.role})"

    @property
    def id(self):
        return self.staff_id

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def manage_inventory(self, book, quantity, action='add'):
        from store.models.book.book import BookInventory
        inventory, _ = BookInventory.objects.get_or_create(book=book)
        previous = inventory.quantity
        if action == 'add':
            inventory.add_stock(quantity)
        else:
            inventory.reduce_stock(quantity)
        InventoryLog.objects.create(
            staff=self, book=book, action=action,
            quantity=quantity, previous_quantity=previous,
            new_quantity=inventory.quantity,
        )

    def get_inventory_logs(self):
        return InventoryLog.objects.filter(staff=self).order_by('-created_at')


class Admin(models.Model):
    """
    Admin model for system administrators.
    Attributes: adminId, username
    Methods: manageSystem()
    """
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    is_superadmin = models.BooleanField(default=False)
    can_manage_staff = models.BooleanField(default=True)
    can_manage_products = models.BooleanField(default=True)
    can_manage_orders = models.BooleanField(default=True)
    can_manage_customers = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'store_admin'
        verbose_name = 'Admin'

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def manage_system(self, action, target_type=None, target_id=None, data=None):
        AdminActionLog.objects.create(
            admin=self, action=action,
            target_type=target_type or '',
            target_id=target_id or 0,
            details=str(data) if data else '',
        )


class InventoryLog(models.Model):
    """
    Inventory log model for tracking inventory changes.
    """
    ACTION_TYPES = [
        ('add', 'Add Stock'),
        ('reduce', 'Reduce Stock'),
        ('adjust', 'Adjust'),
        ('import', 'Import'),
    ]

    log_id = models.AutoField(primary_key=True)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='inventory_logs')
    book = models.ForeignKey('store.Book', on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    quantity = models.IntegerField()
    previous_quantity = models.PositiveIntegerField(default=0)
    new_quantity = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_inventorylog'
        verbose_name = 'Inventory Log'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action}: {self.book} ({self.quantity})"


class AdminActionLog(models.Model):
    """
    Admin action log model for tracking admin activities.
    """
    log_id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, related_name='action_logs')
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50, blank=True, null=True)
    target_id = models.CharField(max_length=50, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_adminactionlog'
        verbose_name = 'Admin Action Log'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.admin} - {self.action}"
