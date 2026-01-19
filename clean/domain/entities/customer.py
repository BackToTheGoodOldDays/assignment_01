"""
Customer Entity - Domain Layer
Represents the Customer business entity independent of any framework.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Customer:
    """Customer entity representing a bookstore customer."""
    
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    password: str = ""
    is_active: bool = True
    date_joined: Optional[datetime] = None
    
    def __post_init__(self):
        if self.date_joined is None:
            self.date_joined = datetime.now()
    
    def validate(self) -> bool:
        """Validate customer data."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Customer name is required")
        if not self.email or "@" not in self.email:
            raise ValueError("Valid email is required")
        if not self.password or len(self.password) < 6:
            raise ValueError("Password must be at least 6 characters")
        return True
    
    def __str__(self):
        return f"Customer({self.name}, {self.email})"
