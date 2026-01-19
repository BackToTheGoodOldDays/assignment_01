"""
Django Customer Repository - Infrastructure Layer
Implementation of CustomerRepositoryInterface using Django ORM.
"""
from typing import Optional, List
from django.contrib.auth.hashers import make_password, check_password
from domain.entities.customer import Customer
from interfaces.repositories.customer_repository import CustomerRepositoryInterface
from framework.models import CustomerModel


class DjangoCustomerRepository(CustomerRepositoryInterface):
    """Django ORM implementation of customer repository."""
    
    def save(self, customer: Customer) -> Customer:
        """Save a customer entity."""
        if customer.id:
            # Update existing
            customer_model = CustomerModel.objects.get(id=customer.id)
            customer_model.name = customer.name
            customer_model.email = customer.email
            if customer.password and not customer.password.startswith('pbkdf2_'):
                customer_model.password = make_password(customer.password)
            customer_model.is_active = customer.is_active
            customer_model.save()
        else:
            # Create new
            customer_model = CustomerModel.objects.create_user(
                email=customer.email,
                name=customer.name,
                password=customer.password
            )
        
        return self._to_entity(customer_model)
    
    def find_by_id(self, customer_id: int) -> Optional[Customer]:
        """Find a customer by ID."""
        try:
            customer_model = CustomerModel.objects.get(id=customer_id)
            return self._to_entity(customer_model)
        except CustomerModel.DoesNotExist:
            return None
    
    def find_by_email(self, email: str) -> Optional[Customer]:
        """Find a customer by email."""
        try:
            customer_model = CustomerModel.objects.get(email=email)
            return self._to_entity(customer_model)
        except CustomerModel.DoesNotExist:
            return None
    
    def find_all(self) -> List[Customer]:
        """Get all customers."""
        return [self._to_entity(c) for c in CustomerModel.objects.all()]
    
    def delete(self, customer_id: int) -> bool:
        """Delete a customer by ID."""
        try:
            CustomerModel.objects.filter(id=customer_id).delete()
            return True
        except:
            return False
    
    def verify_password(self, customer: Customer, password: str) -> bool:
        """Verify customer password."""
        try:
            customer_model = CustomerModel.objects.get(id=customer.id)
            return check_password(password, customer_model.password)
        except CustomerModel.DoesNotExist:
            return False
    
    def _to_entity(self, model: CustomerModel) -> Customer:
        """Convert Django model to domain entity."""
        return Customer(
            id=model.id,
            name=model.name,
            email=model.email,
            password=model.password,
            is_active=model.is_active,
            date_joined=model.date_joined
        )
