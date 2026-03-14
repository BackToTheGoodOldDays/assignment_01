import jwt
import hashlib
import requests
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Manager
from .serializers import ManagerSerializer


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(manager_id, username):
    payload = {
        'manager_id': manager_id,
        'username': username,
        'role': 'manager',
        'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_manager_from_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        manager = Manager.objects.get(username=username, is_active=True)
    except Manager.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    if manager.password != hash_password(password):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    token = generate_token(manager.manager_id, manager.username)
    return Response({'manager': ManagerSerializer(manager).data, 'token': token})


@api_view(['GET', 'POST'])
def manager_list(request):
    if request.method == 'GET':
        managers = Manager.objects.filter(is_active=True)
        return Response(ManagerSerializer(managers, many=True).data)
    # POST - create manager
    username = request.data.get('username')
    name = request.data.get('name')
    email = request.data.get('email')
    password = request.data.get('password')
    if not all([username, name, email, password]):
        return Response({'error': 'username, name, email, and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    if Manager.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
    if Manager.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
    manager = Manager.objects.create(
        username=username,
        name=name,
        email=email,
        password=hash_password(password),
    )
    return Response(ManagerSerializer(manager).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def manager_detail(request, manager_id):
    try:
        manager = Manager.objects.get(manager_id=manager_id)
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(ManagerSerializer(manager).data)
    elif request.method == 'DELETE':
        manager.is_active = False
        manager.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # PUT
    for field in ['name', 'email']:
        if field in request.data:
            setattr(manager, field, request.data[field])
    if 'password' in request.data:
        manager.password = hash_password(request.data['password'])
    manager.save()
    return Response(ManagerSerializer(manager).data)


@api_view(['GET'])
def dashboard(request):
    payload = get_manager_from_token(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    summary = {}

    # Fetch total books
    try:
        response = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                summary['total_books'] = len(data)
            elif isinstance(data, dict) and 'count' in data:
                summary['total_books'] = data['count']
            else:
                summary['total_books'] = 0
        else:
            summary['total_books'] = None
    except Exception:
        summary['total_books'] = None

    # Fetch total orders
    try:
        response = requests.get(f"{settings.ORDER_SERVICE_URL}/api/orders/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                summary['total_orders'] = len(data)
            elif isinstance(data, dict) and 'count' in data:
                summary['total_orders'] = data['count']
            else:
                summary['total_orders'] = 0
        else:
            summary['total_orders'] = None
    except Exception:
        summary['total_orders'] = None

    # Fetch total customers
    try:
        response = requests.get(f"{settings.CUSTOMER_SERVICE_URL}/api/customers/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                summary['total_customers'] = len(data)
            elif isinstance(data, dict) and 'count' in data:
                summary['total_customers'] = data['count']
            else:
                summary['total_customers'] = 0
        else:
            summary['total_customers'] = None
    except Exception:
        summary['total_customers'] = None

    return Response(summary)
