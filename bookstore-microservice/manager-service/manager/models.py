from django.db import models


class Manager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'managers'

    def __str__(self):
        return self.username
