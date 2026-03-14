from django.db import models


class Staff(models.Model):
    ROLES = [('admin', 'Admin'), ('staff', 'Inventory Staff')]
    staff_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLES, default='staff')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staff'

    def __str__(self):
        return self.username


class InventoryLog(models.Model):
    ACTIONS = [('add', 'Add Stock'), ('remove', 'Remove Stock'), ('update', 'Update Info')]
    log_id = models.AutoField(primary_key=True)
    staff_id = models.IntegerField()
    book_id = models.IntegerField()
    action = models.CharField(max_length=20, choices=ACTIONS)
    quantity = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_logs'
