from rest_framework import serializers
from .models import Staff, InventoryLog


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['staff_id', 'username', 'name', 'email', 'role', 'is_active', 'created_at']


class StaffCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['username', 'name', 'email', 'password', 'role']


class InventoryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLog
        fields = '__all__'
