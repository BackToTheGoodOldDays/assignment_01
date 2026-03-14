import jwt
import hashlib
import requests
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Address
from .serializers import CustomerSerializer, CustomerCreateSerializer, AddressSerializer


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(customer_id, email):
    payload = {
        'customer_id': customer_id,
        'email': email,
        'role': 'customer',
        'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_customer_from_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        return None


@api_view(['POST'])
def register(request):
    serializer = CustomerCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    if Customer.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

    customer = Customer.objects.create(
        name=serializer.validated_data['name'],
        email=email,
        phone=serializer.validated_data.get('phone', ''),
        password=hash_password(serializer.validated_data['password']),
    )

    # Create cart for customer
    try:
        requests.post(
            f"{settings.CART_SERVICE_URL}/api/carts/create-for-customer/",
            json={'customer_id': customer.customer_id},
            timeout=5
        )
    except Exception:
        pass  # Non-critical

    token = generate_token(customer.customer_id, customer.email)
    return Response({
        'customer': CustomerSerializer(customer).data,
        'token': token
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customer.objects.get(email=email, is_active=True)
    except Customer.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if customer.password != hash_password(password):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    token = generate_token(customer.customer_id, customer.email)
    return Response({
        'customer': CustomerSerializer(customer).data,
        'token': token
    })


@api_view(['GET', 'PUT'])
def profile(request):
    payload = get_customer_from_token(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        customer = Customer.objects.get(customer_id=payload['customer_id'])
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(CustomerSerializer(customer).data)

    # PUT
    for field in ['name', 'phone']:
        if field in request.data:
            setattr(customer, field, request.data[field])
    customer.save()
    return Response(CustomerSerializer(customer).data)


@api_view(['GET'])
def get_customer_by_id(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        return Response(CustomerSerializer(customer).data)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
def addresses(request):
    payload = get_customer_from_token(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    customer_id = payload['customer_id']

    if request.method == 'GET':
        addr_list = Address.objects.filter(customer_id=customer_id)
        return Response(AddressSerializer(addr_list, many=True).data)

    data = request.data.copy()
    data['customer'] = customer_id
    serializer = AddressSerializer(data=data)
    if serializer.is_valid():
        if data.get('is_default'):
            Address.objects.filter(customer_id=customer_id).update(is_default=False)
        addr = serializer.save()
        return Response(AddressSerializer(addr).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def address_detail(request, address_id):
    payload = get_customer_from_token(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        addr = Address.objects.get(address_id=address_id, customer_id=payload['customer_id'])
    except Address.DoesNotExist:
        return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(AddressSerializer(addr).data)
    elif request.method == 'DELETE':
        addr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT
    serializer = AddressSerializer(addr, data=request.data, partial=True)
    if serializer.is_valid():
        if request.data.get('is_default'):
            Address.objects.filter(customer_id=payload['customer_id']).update(is_default=False)
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_customers(request):
    """For inter-service use."""
    customers = Customer.objects.filter(is_active=True)
    return Response(CustomerSerializer(customers, many=True).data)
