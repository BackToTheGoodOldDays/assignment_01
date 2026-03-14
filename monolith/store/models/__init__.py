"""
Store Models Package
Contains all domain models organized by business domain:
- customer: Customer, User, UserProfile, UserRole, UserStatus, LoginSession
- book: Book, Author, Category, Publisher, BookImage, BookDescription, BookStatus, BookRating, BookTag, BookInventory
- order: Cart, CartItem, Order, OrderItem, Payment, Shipping, etc.
- staff: Staff, Admin
- review: Rating, Review, Recommendation, etc.
"""

from .customer import (
    Customer, CustomerManager,
    User, UserManager, UserProfile, UserRole, UserStatus, LoginSession,
)

from .book import (
    Book, Author, Category, Publisher, BookImage,
    BookDescription, BookStatus, BookRating, BookTag, BookInventory,
)

from .order import (
    Cart, CartItem, CartStatus, CartSummary, SavedCart, CartHistory,
    Order, OrderItem, OrderStatus, OrderHistory, Invoice, OrderNote,
    OrderSummary, OrderTracking, OrderCancellation,
    Payment, PaymentMethod, PaymentStatus, Transaction, PaymentReceipt, Refund,
    Shipping, ShippingMethod, ShippingStatus, DeliveryAddress, Shipment, DeliveryTracking,
)

from .staff import Staff, Admin, InventoryLog, AdminActionLog

from .review import (
    Rating, Review, UserBehavior, PurchaseHistory,
    RecommendationRule, Recommendation,
)

__all__ = [
    'Customer', 'CustomerManager', 'User', 'UserManager', 'UserProfile',
    'UserRole', 'UserStatus', 'LoginSession',
    'Book', 'Author', 'Category', 'Publisher', 'BookImage',
    'BookDescription', 'BookStatus', 'BookRating', 'BookTag', 'BookInventory',
    'Cart', 'CartItem', 'CartStatus', 'CartSummary', 'SavedCart', 'CartHistory',
    'Order', 'OrderItem', 'OrderStatus', 'OrderHistory', 'Invoice', 'OrderNote',
    'OrderSummary', 'OrderTracking', 'OrderCancellation',
    'Payment', 'PaymentMethod', 'PaymentStatus', 'Transaction', 'PaymentReceipt', 'Refund',
    'Shipping', 'ShippingMethod', 'ShippingStatus', 'DeliveryAddress', 'Shipment', 'DeliveryTracking',
    'Staff', 'Admin', 'InventoryLog', 'AdminActionLog',
    'Rating', 'Review', 'UserBehavior', 'PurchaseHistory', 'RecommendationRule', 'Recommendation',
]
