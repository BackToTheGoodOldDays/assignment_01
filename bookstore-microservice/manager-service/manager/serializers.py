from rest_framework import serializers
from .models import Manager


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['manager_id', 'username', 'name', 'email', 'is_active', 'created_at']
