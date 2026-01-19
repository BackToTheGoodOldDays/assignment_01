"""
Customer Use Cases - Application Layer
Contains application-specific business logic for customer operations.
"""
from typing import Optional
from domain.entities.customer import Customer
from interfaces.repositories.customer_repository import CustomerRepositoryInterface


class RegisterCustomerUseCase:
    """Use case for customer registration."""
    
    def __init__(self, customer_repository: CustomerRepositoryInterface):
        self.customer_repository = customer_repository
    
    def execute(self, name: str, email: str, password: str) -> Customer:
        """
        Register a new customer.
        
        Args:
            name: Customer's full name
            email: Customer's email address
            password: Customer's password
            
        Returns:
            Created Customer entity
            
        Raises:
            ValueError: If validation fails or email already exists
        """
        # Check if email already exists
        existing_customer = self.customer_repository.find_by_email(email)
        if existing_customer:
            raise ValueError("A customer with this email already exists")
        
        # Create and validate customer entity
        customer = Customer(name=name, email=email, password=password)
        customer.validate()
        
        # Save and return
        return self.customer_repository.save(customer)


class AuthenticateCustomerUseCase:
    """Use case for customer authentication."""
    
    def __init__(self, customer_repository: CustomerRepositoryInterface):
        self.customer_repository = customer_repository
    
    def execute(self, email: str, password: str) -> Optional[Customer]:
        """
        Authenticate a customer with email and password.
        
        Args:
            email: Customer's email address
            password: Customer's password
            
        Returns:
            Customer entity if authentication successful, None otherwise
        """
        customer = self.customer_repository.find_by_email(email)
        if customer and self.customer_repository.verify_password(customer, password):
            return customer
        return None


class GetCustomerByIdUseCase:
    """Use case for retrieving a customer by ID."""
    
    def __init__(self, customer_repository: CustomerRepositoryInterface):
        self.customer_repository = customer_repository
    
    def execute(self, customer_id: int) -> Optional[Customer]:
        """
        Get a customer by their ID.
        
        Args:
            customer_id: The customer's ID
            
        Returns:
            Customer entity if found, None otherwise
        """
        return self.customer_repository.find_by_id(customer_id)


class GetCustomerByEmailUseCase:
    """Use case for retrieving a customer by email."""
    
    def __init__(self, customer_repository: CustomerRepositoryInterface):
        self.customer_repository = customer_repository
    
    def execute(self, email: str) -> Optional[Customer]:
        """
        Get a customer by their email.
        
        Args:
            email: The customer's email address
            
        Returns:
            Customer entity if found, None otherwise
        """
        return self.customer_repository.find_by_email(email)
