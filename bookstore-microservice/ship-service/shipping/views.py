from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status
from .models import ShippingMethod, Shipment
from .serializers import ShippingMethodSerializer, ShipmentSerializer


class ShippingMethodViewSet(viewsets.ModelViewSet):
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.select_related('shipping_method').all()
    serializer_class = ShipmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            qs = qs.filter(order_id=order_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(tracking_number=Shipment.generate_tracking_number())

    @action(detail=True, methods=['put', 'patch'])
    def update_status(self, request, pk=None):
        shipment = self.get_object()
        new_status = request.data.get('status')
        valid_statuses = [s[0] for s in Shipment.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({'error': f'Invalid status. Valid: {valid_statuses}'}, status=400)
        shipment.status = new_status
        if new_status == 'shipped':
            shipment.shipped_at = timezone.now()
        elif new_status == 'delivered':
            shipment.delivered_at = timezone.now()
        shipment.save()
        return Response(ShipmentSerializer(shipment).data)
