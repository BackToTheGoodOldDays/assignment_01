"""
Service Clients for communicating with microservices.
This module handles all HTTP requests to backend services.
"""
import requests
from django.conf import settings


class ServiceClient:
    """Base client for microservice communication."""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.timeout = 5
    
    def get(self, endpoint, params=None):
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Service error: {e}")
            return None
    
    def post(self, endpoint, data=None):
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=data,
                timeout=self.timeout
            )
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            print(f"Service error: {e}")
            return None, 500


class CustomerServiceClient(ServiceClient):
    """Client for Customer Service."""
    
    def __init__(self):
        super().__init__(settings.CUSTOMER_SERVICE_URL)
    
    def register(self, name, email, password, password_confirm):
        data = {
            'name': name,
            'email': email,
            'password': password,
            'password_confirm': password_confirm
        }
        return self.post('/api/customers/register/', data)
    
    def login(self, email, password):
        data = {'email': email, 'password': password}
        return self.post('/api/customers/login/', data)
    
    def get_customer(self, customer_id):
        return self.get(f'/api/customers/{customer_id}/')
    
    def health_check(self):
        return self.get('/api/customers/health/')


class BookServiceClient(ServiceClient):
    """Client for Book Service."""
    
    def __init__(self):
        super().__init__(settings.BOOK_SERVICE_URL)
    
    def get_all_books(self, search=None):
        params = {'search': search} if search else None
        return self.get('/api/books/', params)
    
    def get_book(self, book_id):
        return self.get(f'/api/books/{book_id}/')
    
    def health_check(self):
        return self.get('/api/books/health/')


class CartServiceClient(ServiceClient):
    """Client for Cart Service."""
    
    def __init__(self):
        super().__init__(settings.CART_SERVICE_URL)
    
    def get_cart(self, customer_id):
        return self.get('/api/cart/by_customer/', {'customer_id': customer_id})
    
    def add_item(self, customer_id, book_id, quantity=1):
        data = {
            'customer_id': customer_id,
            'book_id': book_id,
            'quantity': quantity
        }
        return self.post('/api/cart/add_item/', data)
    
    def update_item(self, customer_id, book_id, quantity):
        data = {
            'customer_id': customer_id,
            'book_id': book_id,
            'quantity': quantity
        }
        return self.post('/api/cart/update_item/', data)
    
    def remove_item(self, customer_id, book_id):
        data = {
            'customer_id': customer_id,
            'book_id': book_id
        }
        return self.post('/api/cart/remove_item/', data)
    
    def clear_cart(self, customer_id):
        data = {'customer_id': customer_id}
        return self.post('/api/cart/clear/', data)
    
    def health_check(self):
        return self.get('/api/cart/health/')


# Singleton instances
customer_client = CustomerServiceClient()
book_client = BookServiceClient()
cart_client = CartServiceClient()
