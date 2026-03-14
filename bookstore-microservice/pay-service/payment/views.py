from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PaymentMethod, Payment
from .serializers import PaymentMethodSerializer, PaymentSerializer


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('payment_method').all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            qs = qs.filter(order_id=order_id)
        return qs

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process/complete a payment."""
        payment = self.get_object()
        if payment.status == 'completed':
            return Response({'error': 'Payment already completed'}, status=400)
        payment.status = 'completed'
        payment.transaction_id = Payment.generate_transaction_id()
        payment.paid_at = timezone.now()
        payment.save()
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        if payment.status != 'completed':
            return Response({'error': 'Only completed payments can be refunded'}, status=400)
        payment.status = 'refunded'
        payment.save()
        return Response(PaymentSerializer(payment).data)
