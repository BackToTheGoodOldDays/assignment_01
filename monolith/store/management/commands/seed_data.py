"""
Management command to seed initial data for the bookstore.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from store.models.book.book import (
    Author, Category, Publisher, BookStatus, BookTag, Book,
    BookDescription, BookInventory, BookImage,
)
from store.models.order.order import OrderStatus, PaymentMethod, PaymentStatus, ShippingMethod, ShippingStatus
from store.models.order.cart import CartStatus
from store.models.staff.staff import Staff
from store.models.customer.customer import Customer


class Command(BaseCommand):
    help = 'Seed initial data for the bookstore'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Cart statuses
        for name in ['Active', 'Completed', 'Abandoned', 'Saved']:
            CartStatus.objects.get_or_create(name=name)
        self.stdout.write('  Cart statuses created')

        # Order statuses
        for i, name in enumerate(['Pending', 'Confirmed', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Refunded']):
            OrderStatus.objects.get_or_create(name=name, defaults={'sort_order': i, 'color': 'blue'})
        self.stdout.write('  Order statuses created')

        # Book statuses
        for name in ['Available', 'Out of Stock', 'Pre-order', 'Discontinued']:
            BookStatus.objects.get_or_create(status_name=name)
        self.stdout.write('  Book statuses created')

        # Payment methods
        for code, name in [('cod', 'Cash on Delivery'), ('bank', 'Bank Transfer'), ('momo', 'MoMo'), ('zalopay', 'ZaloPay')]:
            PaymentMethod.objects.get_or_create(code=code, defaults={'name': name, 'is_active': True})
        self.stdout.write('  Payment methods created')

        # Payment statuses
        for name in ['Pending', 'Processing', 'Completed', 'Failed', 'Refunded']:
            PaymentStatus.objects.get_or_create(name=name)
        self.stdout.write('  Payment statuses created')

        # Shipping methods
        for code, name, fee in [('standard', 'Standard Shipping', 30000), ('express', 'Express Shipping', 50000), ('same_day', 'Same Day', 80000)]:
            ShippingMethod.objects.get_or_create(code=code, defaults={
                'name': name, 'base_fee': fee, 'is_active': True,
                'estimated_days_min': 1, 'estimated_days_max': 5,
            })
        self.stdout.write('  Shipping methods created')

        # Shipping statuses
        for i, name in enumerate(['Pending', 'Picked Up', 'In Transit', 'Out for Delivery', 'Delivered', 'Failed']):
            ShippingStatus.objects.get_or_create(name=name, defaults={'sort_order': i})
        self.stdout.write('  Shipping statuses created')

        # Categories
        categories = {}
        for name in ['Fiction', 'Non-Fiction', 'Science', 'Technology', 'History', 'Children', 'Comics', 'Education']:
            cat, _ = Category.objects.get_or_create(name=name)
            categories[name] = cat
        self.stdout.write('  Categories created')

        # Publishers
        publishers = {}
        for name in ['NXB Kim Dong', 'NXB Tre', 'NXB Tong Hop', 'NXB Giao Duc', 'NXB Van Hoc']:
            pub, _ = Publisher.objects.get_or_create(name=name)
            publishers[name] = pub
        self.stdout.write('  Publishers created')

        # Authors
        authors = {}
        for name in ['Nguyen Nhat Anh', 'To Hoai', 'Nam Cao', 'Nguyen Du', 'Dale Carnegie']:
            author, _ = Author.objects.get_or_create(name=name)
            authors[name] = author
        self.stdout.write('  Authors created')

        # Tags
        tags = {}
        for name in ['Bestseller', 'New', 'Sale', 'Recommended', 'Classic']:
            tag, _ = BookTag.objects.get_or_create(name=name)
            tags[name] = tag
        self.stdout.write('  Tags created')

        available_status = BookStatus.objects.filter(status_name='Available').first()

        # Sample books
        sample_books = [
            {'title': 'Cho toi xin mot ve di tuoi tho', 'isbn': '978-604-1-00001', 'price': Decimal('85000'), 'author': 'Nguyen Nhat Anh', 'category': 'Fiction', 'publisher': 'NXB Tre'},
            {'title': 'De men phieu luu ky', 'isbn': '978-604-1-00002', 'price': Decimal('65000'), 'author': 'To Hoai', 'category': 'Children', 'publisher': 'NXB Kim Dong'},
            {'title': 'Chi Pheo', 'isbn': '978-604-1-00003', 'price': Decimal('45000'), 'author': 'Nam Cao', 'category': 'Fiction', 'publisher': 'NXB Van Hoc'},
            {'title': 'Truyen Kieu', 'isbn': '978-604-1-00004', 'price': Decimal('95000'), 'author': 'Nguyen Du', 'category': 'Fiction', 'publisher': 'NXB Van Hoc'},
            {'title': 'Dac Nhan Tam', 'isbn': '978-604-1-00005', 'price': Decimal('120000'), 'author': 'Dale Carnegie', 'category': 'Non-Fiction', 'publisher': 'NXB Tong Hop'},
            {'title': 'Mat biec', 'isbn': '978-604-1-00006', 'price': Decimal('79000'), 'author': 'Nguyen Nhat Anh', 'category': 'Fiction', 'publisher': 'NXB Tre'},
            {'title': 'Toi thay hoa vang tren co xanh', 'isbn': '978-604-1-00007', 'price': Decimal('72000'), 'author': 'Nguyen Nhat Anh', 'category': 'Fiction', 'publisher': 'NXB Tre'},
            {'title': 'Lap trinh Python co ban', 'isbn': '978-604-1-00008', 'price': Decimal('150000'), 'author': 'Dale Carnegie', 'category': 'Technology', 'publisher': 'NXB Giao Duc'},
        ]

        for data in sample_books:
            book, created = Book.objects.get_or_create(
                isbn=data['isbn'],
                defaults={
                    'title': data['title'],
                    'price': data['price'],
                    'author': authors.get(data['author']),
                    'category': categories.get(data['category']),
                    'publisher': publishers.get(data['publisher']),
                    'status': available_status,
                }
            )
            if created:
                BookInventory.objects.get_or_create(book=book, defaults={'quantity': 50})
                BookDescription.objects.get_or_create(
                    book=book,
                    defaults={'content': f'Description for {data["title"]}', 'short_description': data['title']}
                )
        self.stdout.write('  Books created')

        # Admin staff
        staff, created = Staff.objects.get_or_create(
            email='admin@bookstore.com',
            defaults={
                'name': 'Admin Staff',
                'role': 'manager',
                'employee_code': 'EMP001',
            }
        )
        if created:
            staff.set_password('admin123')
        self.stdout.write('  Staff created')

        # Test customer
        if not Customer.objects.filter(email='test@test.com').exists():
            Customer.objects.create_user(
                email='test@test.com',
                name='Test Customer',
                password='test123',
                phone='0123456789',
            )
        self.stdout.write('  Test customer created')

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
