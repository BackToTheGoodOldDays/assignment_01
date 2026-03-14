from rest_framework import serializers
from .models import PaymentMethod, Payment


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
