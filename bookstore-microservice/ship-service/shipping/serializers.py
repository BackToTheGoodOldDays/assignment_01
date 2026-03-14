from rest_framework import serializers
from .models import ShippingMethod, Shipment


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = '__all__'


class ShipmentSerializer(serializers.ModelSerializer):
    shipping_method_name = serializers.CharField(source='shipping_method.name', read_only=True)

    class Meta:
        model = Shipment
        fields = '__all__'
