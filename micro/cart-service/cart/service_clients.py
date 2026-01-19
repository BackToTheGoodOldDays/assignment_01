"""
Service clients for communicating with other microservices.
"""
import requests
from django.conf import settings


class CustomerServiceClient:
    """Client for communicating with customer-service."""
    
    BASE_URL = getattr(settings, 'CUSTOMER_SERVICE_URL', 'http://localhost:8001/api/customers')
    
    @classmethod
    def verify_customer(cls, customer_id):
        """Verify if a customer exists."""
        try:
            response = requests.get(f"{cls.BASE_URL}/{customer_id}/verify/", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    @classmethod
    def get_customer(cls, customer_id):
        """Get customer details."""
        try:
            response = requests.get(f"{cls.BASE_URL}/{customer_id}/", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None


class BookServiceClient:
    """Client for communicating with book-service."""
    
    BASE_URL = getattr(settings, 'BOOK_SERVICE_URL', 'http://localhost:8002/api/books')
    
    @classmethod
    def get_book(cls, book_id):
        """Get book details."""
        try:
            response = requests.get(f"{cls.BASE_URL}/{book_id}/", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    @classmethod
    def check_availability(cls, book_id):
        """Check book availability."""
        try:
            response = requests.get(f"{cls.BASE_URL}/{book_id}/check_availability/", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    @classmethod
    def update_stock(cls, book_id, quantity, operation='decrease'):
        """Update book stock."""
        try:
            response = requests.post(
                f"{cls.BASE_URL}/{book_id}/update_stock/",
                json={'quantity': quantity, 'operation': operation},
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
