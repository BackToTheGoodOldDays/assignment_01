from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import Customer
from .serializers import (
    CustomerSerializer, 
    CustomerRegistrationSerializer,
    CustomerLoginSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer CRUD operations."""
    
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new customer."""
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(
                CustomerSerializer(customer).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Authenticate a customer."""
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            customer = authenticate(request, username=email, password=password)
            if customer:
                return Response({
                    'message': 'Login successful',
                    'customer_id': customer.id,
                    'name': customer.name,
                    'email': customer.email
                })
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """Verify if a customer exists (for other services)."""
        try:
            customer = Customer.objects.get(pk=pk)
            return Response({
                'exists': True,
                'customer': CustomerSerializer(customer).data
            })
        except Customer.DoesNotExist:
            return Response(
                {'exists': False},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint for the service."""
    return Response({'status': 'healthy', 'service': 'customer-service'})
