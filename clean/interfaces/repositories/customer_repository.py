"""
Customer Repository Interface - Interfaces Layer
Defines the contract for customer data access.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.customer import Customer


class CustomerRepositoryInterface(ABC):
    """Abstract interface for customer repository operations."""
    
    @abstractmethod
    def save(self, customer: Customer) -> Customer:
        """Save a customer entity."""
        pass
    
    @abstractmethod
    def find_by_id(self, customer_id: int) -> Optional[Customer]:
        """Find a customer by ID."""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Customer]:
        """Find a customer by email."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Customer]:
        """Get all customers."""
        pass
    
    @abstractmethod
    def delete(self, customer_id: int) -> bool:
        """Delete a customer by ID."""
        pass
    
    @abstractmethod
    def verify_password(self, customer: Customer, password: str) -> bool:
        """Verify customer password."""
        pass
