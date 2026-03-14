import jwt
import hashlib
import requests
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Staff, InventoryLog
from .serializers import StaffSerializer, StaffCreateSerializer, InventoryLogSerializer


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(staff_id, username, role):
    payload = {
        'staff_id': staff_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def get_staff_from_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    except Exception:
        return None


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    try:
        staff = Staff.objects.get(username=username, is_active=True)
    except Staff.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=401)
    if staff.password != hash_password(password):
        return Response({'error': 'Invalid credentials'}, status=401)
    token = generate_token(staff.staff_id, staff.username, staff.role)
    return Response({'staff': StaffSerializer(staff).data, 'token': token})


@api_view(['GET', 'POST'])
def staff_list(request):
    if request.method == 'GET':
        staff = Staff.objects.filter(is_active=True)
        return Response(StaffSerializer(staff, many=True).data)
    # POST - create staff
    serializer = StaffCreateSerializer(data=request.data)
    if serializer.is_valid():
        if Staff.objects.filter(username=serializer.validated_data['username']).exists():
            return Response({'error': 'Username taken'}, status=400)
        s = Staff.objects.create(
            username=serializer.validated_data['username'],
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            password=hash_password(serializer.validated_data['password']),
            role=serializer.validated_data.get('role', 'staff'),
        )
        return Response(StaffSerializer(s).data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def staff_detail(request, staff_id):
    try:
        staff = Staff.objects.get(staff_id=staff_id)
    except Staff.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    if request.method == 'GET':
        return Response(StaffSerializer(staff).data)
    elif request.method == 'DELETE':
        staff.is_active = False
        staff.save()
        return Response(status=204)
    for field in ['name', 'email', 'role']:
        if field in request.data:
            setattr(staff, field, request.data[field])
    staff.save()
    return Response(StaffSerializer(staff).data)


@api_view(['GET', 'POST'])
def inventory_logs(request):
    if request.method == 'GET':
        logs = InventoryLog.objects.all().order_by('-created_at')
        staff_id = request.query_params.get('staff_id')
        book_id = request.query_params.get('book_id')
        if staff_id:
            logs = logs.filter(staff_id=staff_id)
        if book_id:
            logs = logs.filter(book_id=book_id)
        return Response(InventoryLogSerializer(logs, many=True).data)
    serializer = InventoryLogSerializer(data=request.data)
    if serializer.is_valid():
        log = serializer.save()
        return Response(InventoryLogSerializer(log).data, status=201)
    return Response(serializer.errors, status=400)
