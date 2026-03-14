"""
Functional tests for 5 key business flows:
1. Customer registration automatically creates a cart
2. Staff manages books (add book, import stock)
3. Customer adds books to cart, views cart, updates cart
4. Order triggers payment and shipping
5. Customer can rate books
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from store.models.customer.customer import Customer
from store.models.book.book import Book, Author, Category, Publisher, BookStatus, BookInventory, BookDescription
from store.models.order.cart import Cart, CartItem, CartStatus
from store.models.order.order import (
    Order, OrderStatus, OrderItem, Payment, PaymentMethod, PaymentStatus,
    Shipping, ShippingMethod, DeliveryAddress,
)
from store.models.review.review import Rating, Review
from store.models.staff.staff import Staff


class BaseTestCase(TestCase):
    """Shared setup for all test cases."""

    @classmethod
    def setUpTestData(cls):
        # Statuses
        cls.cart_status_active = CartStatus.objects.create(name='Active')
        cls.cart_status_completed = CartStatus.objects.create(name='Completed')
        cls.order_status_pending = OrderStatus.objects.create(name='Pending')
        cls.book_status = BookStatus.objects.create(status_name='Available')

        # Payment & Shipping
        cls.payment_status_pending = PaymentStatus.objects.create(name='Pending')
        cls.payment_status_completed = PaymentStatus.objects.create(name='Completed')
        cls.payment_method = PaymentMethod.objects.create(
            name='COD', code='cod', is_active=True, processing_fee=0
        )
        cls.shipping_method = ShippingMethod.objects.create(
            name='Standard', code='standard', base_fee=30000, is_active=True,
            estimated_days_min=3, estimated_days_max=5,
        )

        # Book data
        cls.author = Author.objects.create(name='Nguyen Nhat Anh')
        cls.category = Category.objects.create(name='Van hoc')
        cls.publisher = Publisher.objects.create(name='NXB Tre')

        cls.book1 = Book.objects.create(
            title='Mat Biec', isbn='978-0-001', price=Decimal('85000'),
            author=cls.author, category=cls.category, publisher=cls.publisher,
            status=cls.book_status,
        )
        BookInventory.objects.create(book=cls.book1, quantity=100)

        cls.book2 = Book.objects.create(
            title='Toi Thay Hoa Vang', isbn='978-0-002', price=Decimal('75000'),
            author=cls.author, category=cls.category, publisher=cls.publisher,
            status=cls.book_status,
        )
        BookInventory.objects.create(book=cls.book2, quantity=50)

        # Staff
        cls.staff = Staff.objects.create(
            name='Admin Staff', email='staff@test.com', role='manager', is_active=True,
        )
        cls.staff.set_password('staff123')


class Test1_RegistrationCreatesCart(BaseTestCase):
    """Flow 1: Customer registration automatically creates a cart."""

    def test_register_then_access_cart(self):
        """After registering, visiting cart page auto-creates an active cart."""
        client = Client()

        # Register a new customer
        resp = client.post(reverse('customer:register'), {
            'name': 'New Customer',
            'email': 'newcustomer@test.com',
            'phone': '0901234567',
            'address': '123 Test Street',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        # Should redirect to catalog on success
        self.assertEqual(resp.status_code, 302)

        customer = Customer.objects.get(email='newcustomer@test.com')
        self.assertIsNotNone(customer)

        # No cart exists yet
        self.assertFalse(Cart.objects.filter(customer=customer).exists())

        # Visit cart page - this triggers get_or_create_active_cart
        resp = client.get(reverse('cart:view'))
        self.assertEqual(resp.status_code, 200)

        # Now an active cart exists
        cart = Cart.objects.filter(customer=customer, is_active=True).first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.status.name, 'Active')

    def test_get_active_cart_method(self):
        """Customer.get_active_cart() creates a cart if none exists."""
        customer = Customer.objects.create_user(
            email='carttest@test.com', name='Cart Tester', password='TestPass123!'
        )
        # No cart yet
        self.assertFalse(Cart.objects.filter(customer=customer).exists())

        # Call get_active_cart
        cart = customer.get_active_cart()
        self.assertIsNotNone(cart)
        self.assertTrue(cart.is_active)
        self.assertEqual(cart.customer, customer)

        # Calling again returns the same cart
        cart2 = customer.get_active_cart()
        self.assertEqual(cart.cart_id, cart2.cart_id)


class Test2_StaffManagesBooks(BaseTestCase):
    """Flow 2: Staff manages books (add book, import stock)."""

    def _staff_login(self, client):
        """Login as staff via session."""
        client.post(reverse('staff:login'), {
            'email': 'staff@test.com',
            'password': 'staff123',
        })

    def test_staff_add_book(self):
        """Staff can add a new book to inventory."""
        client = Client()
        self._staff_login(client)

        resp = client.post(reverse('staff:add_book'), {
            'title': 'New Test Book',
            'isbn': '978-0-TEST-001',
            'author': self.author.author_id,
            'category': self.category.category_id,
            'publisher': self.publisher.publisher_id,
            'price': '120000',
            'stock_quantity': '50',
            'description': 'A great test book',
            'short_description': 'Test book',
        })
        self.assertEqual(resp.status_code, 302)  # redirect to inventory_list

        book = Book.objects.filter(isbn='978-0-TEST-001').first()
        self.assertIsNotNone(book)
        self.assertEqual(book.title, 'New Test Book')
        self.assertEqual(book.price, Decimal('120000'))

        # Inventory created
        self.assertEqual(book.inventory.quantity, 50)

        # Description created
        desc = BookDescription.objects.filter(book=book).first()
        self.assertIsNotNone(desc)
        self.assertEqual(desc.short_description, 'Test book')

    def test_staff_import_stock(self):
        """Staff can import additional stock for an existing book."""
        client = Client()
        self._staff_login(client)

        original_qty = self.book1.inventory.quantity  # 100

        resp = client.post(reverse('staff:import_stock'), {
            'import_type': 'single',
            'book': self.book1.book_id,
            'quantity': '25',
            'notes': 'Restock',
        })
        self.assertEqual(resp.status_code, 302)

        self.book1.inventory.refresh_from_db()
        self.assertEqual(self.book1.inventory.quantity, original_qty + 25)


class Test3_CartOperations(BaseTestCase):
    """Flow 3: Customer adds books to cart, views cart, updates cart."""

    def setUp(self):
        self.customer = Customer.objects.create_user(
            email='shopper@test.com', name='Shopper', password='TestPass123!'
        )
        self.client = Client()
        self.client.login(username='shopper@test.com', password='TestPass123!')

    def test_add_book_to_cart(self):
        """Customer can add a book to their cart."""
        resp = self.client.post(
            reverse('cart:add', args=[self.book1.book_id]),
            {'quantity': '2'}
        )
        self.assertEqual(resp.status_code, 302)

        cart = Cart.objects.get(customer=self.customer, is_active=True)
        item = CartItem.objects.get(cart=cart, book=self.book1)
        self.assertEqual(item.quantity, 2)

    def test_view_cart(self):
        """Customer can view their cart."""
        # Add item first
        cart = Cart.get_or_create_active_cart(self.customer)
        CartItem.objects.create(cart=cart, book=self.book1, quantity=1)

        resp = self.client.get(reverse('cart:view'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.book1.title)

    def test_update_cart_quantity(self):
        """Customer can update item quantity in cart."""
        cart = Cart.get_or_create_active_cart(self.customer)
        item = CartItem.objects.create(cart=cart, book=self.book1, quantity=1)

        resp = self.client.post(
            reverse('cart:update', args=[item.item_id]),
            {'quantity': '5'}
        )
        self.assertEqual(resp.status_code, 302)

        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_remove_from_cart(self):
        """Customer can remove an item from cart."""
        cart = Cart.get_or_create_active_cart(self.customer)
        item = CartItem.objects.create(cart=cart, book=self.book1, quantity=3)

        resp = self.client.post(reverse('cart:remove', args=[item.item_id]))
        self.assertEqual(resp.status_code, 302)

        self.assertFalse(CartItem.objects.filter(item_id=item.item_id).exists())

    def test_cart_total_calculation(self):
        """Cart correctly calculates total price."""
        cart = Cart.get_or_create_active_cart(self.customer)
        CartItem.objects.create(cart=cart, book=self.book1, quantity=2)  # 85000 * 2
        CartItem.objects.create(cart=cart, book=self.book2, quantity=1)  # 75000 * 1

        expected = Decimal('85000') * 2 + Decimal('75000')
        self.assertEqual(cart.calculate_total(), expected)

    def test_add_multiple_books(self):
        """Cart handles adding multiple different books."""
        self.client.post(reverse('cart:add', args=[self.book1.book_id]), {'quantity': '1'})
        self.client.post(reverse('cart:add', args=[self.book2.book_id]), {'quantity': '3'})

        cart = Cart.objects.get(customer=self.customer, is_active=True)
        self.assertEqual(cart.items.count(), 2)

        item1 = CartItem.objects.get(cart=cart, book=self.book1)
        item2 = CartItem.objects.get(cart=cart, book=self.book2)
        self.assertEqual(item1.quantity, 1)
        self.assertEqual(item2.quantity, 3)


class Test4_OrderPaymentShipping(BaseTestCase):
    """Flow 4: Order triggers payment and shipping, customer selects pay/ship."""

    def setUp(self):
        self.customer = Customer.objects.create_user(
            email='buyer@test.com', name='Buyer', password='TestPass123!'
        )
        self.client = Client()
        self.client.login(username='buyer@test.com', password='TestPass123!')

        # Prepare cart with items
        self.cart = Cart.get_or_create_active_cart(self.customer)
        CartItem.objects.create(cart=self.cart, book=self.book1, quantity=2)
        CartItem.objects.create(cart=self.cart, book=self.book2, quantity=1)

        # Create delivery address
        self.address = DeliveryAddress.objects.create(
            customer=self.customer,
            recipient_name='Buyer Name',
            phone='0912345678',
            address_line1='456 Main St',
            city='Ho Chi Minh',
            district='Quan 1',
            ward='Phuong Ben Nghe',
            is_default=True,
        )

    def test_checkout_page(self):
        """Checkout page shows shipping methods and payment methods."""
        resp = self.client.get(reverse('cart:checkout'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Standard')  # shipping method
        self.assertContains(resp, 'COD')       # payment method

    def test_create_order_triggers_payment_and_shipping(self):
        """Creating an order also creates Payment and Shipping records."""
        resp = self.client.post(reverse('cart:create'), {
            'shipping_method': self.shipping_method.method_id,
            'payment_method': self.payment_method.method_id,
            'address_id': self.address.address_id,
        })
        self.assertEqual(resp.status_code, 302)

        # Order created
        order = Order.objects.filter(customer=self.customer).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status.name, 'Pending')
        self.assertEqual(order.items.count(), 2)

        # Subtotal = 85000*2 + 75000*1 = 245000
        self.assertEqual(order.subtotal, Decimal('245000'))

        # Payment created
        payment = Payment.objects.filter(order=order).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.method.code, 'cod')
        self.assertEqual(payment.status.name, 'Pending')
        self.assertEqual(payment.amount, order.total_price)

        # Shipping created
        shipping = Shipping.objects.filter(order=order).first()
        self.assertIsNotNone(shipping)
        self.assertEqual(shipping.method.code, 'standard')
        self.assertEqual(shipping.fee, Decimal('30000'))
        self.assertEqual(shipping.delivery_address, self.address)

        # Total = subtotal + shipping
        self.assertEqual(order.total_price, Decimal('275000'))

        # Cart deactivated
        self.cart.refresh_from_db()
        self.assertFalse(self.cart.is_active)

    def test_process_payment(self):
        """Customer can process payment for an order."""
        # Create the order first
        self.client.post(reverse('cart:create'), {
            'shipping_method': self.shipping_method.method_id,
            'payment_method': self.payment_method.method_id,
            'address_id': self.address.address_id,
        })
        order = Order.objects.get(customer=self.customer)
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.status.name, 'Pending')

        # Process payment
        resp = self.client.post(reverse('cart:payment', args=[order.order_id]))
        self.assertEqual(resp.status_code, 302)

        payment.refresh_from_db()
        self.assertEqual(payment.status.name, 'Completed')
        self.assertIsNotNone(payment.transaction_id)
        self.assertIsNotNone(payment.payment_date)

    def test_order_with_new_address(self):
        """Customer can create an order with a new address inline."""
        resp = self.client.post(reverse('cart:create'), {
            'shipping_method': self.shipping_method.method_id,
            'payment_method': self.payment_method.method_id,
            'recipient_name': 'New Recipient',
            'phone': '0999888777',
            'address_line1': '789 New Street',
            'city': 'Ha Noi',
            'district': 'Hoan Kiem',
            'ward': 'Phuong Hang Bai',
        })
        self.assertEqual(resp.status_code, 302)

        order = Order.objects.filter(customer=self.customer).first()
        shipping = Shipping.objects.get(order=order)
        self.assertEqual(shipping.delivery_address.recipient_name, 'New Recipient')
        self.assertEqual(shipping.delivery_address.city, 'Ha Noi')


class Test5_CustomerRatesBooks(BaseTestCase):
    """Flow 5: Customer can rate books after purchase."""

    def setUp(self):
        self.customer = Customer.objects.create_user(
            email='reviewer@test.com', name='Reviewer', password='TestPass123!'
        )
        self.client = Client()
        self.client.login(username='reviewer@test.com', password='TestPass123!')

        # Create a completed order so the customer can rate
        cart = Cart.get_or_create_active_cart(self.customer)
        CartItem.objects.create(cart=cart, book=self.book1, quantity=1)
        self.order = Order.place_order(customer=self.customer, cart=cart)

    def test_rate_book(self):
        """Customer can rate a book from their order."""
        resp = self.client.post(
            reverse('cart:rate_book', args=[self.order.order_id, self.book1.book_id]),
            {'rating': '4'}
        )
        self.assertEqual(resp.status_code, 302)

        rating = Rating.objects.get(customer=self.customer, book=self.book1)
        self.assertEqual(rating.score, 4)

    def test_rate_book_with_review(self):
        """Customer can rate a book and leave a review."""
        resp = self.client.post(
            reverse('cart:rate_book', args=[self.order.order_id, self.book1.book_id]),
            {'rating': '5', 'review': 'Excellent book, highly recommended!'}
        )
        self.assertEqual(resp.status_code, 302)

        rating = Rating.objects.get(customer=self.customer, book=self.book1)
        self.assertEqual(rating.score, 5)

        review = Review.objects.get(customer=self.customer, book=self.book1)
        self.assertEqual(review.content, 'Excellent book, highly recommended!')
        self.assertTrue(review.is_verified_purchase)

    def test_update_rating(self):
        """Customer can update their rating for a book."""
        # Rate once
        self.client.post(
            reverse('cart:rate_book', args=[self.order.order_id, self.book1.book_id]),
            {'rating': '3'}
        )
        # Update rating
        self.client.post(
            reverse('cart:rate_book', args=[self.order.order_id, self.book1.book_id]),
            {'rating': '5'}
        )

        # Only one rating record, updated to 5
        self.assertEqual(Rating.objects.filter(customer=self.customer, book=self.book1).count(), 1)
        rating = Rating.objects.get(customer=self.customer, book=self.book1)
        self.assertEqual(rating.score, 5)

    def test_write_review(self):
        """Customer can write a detailed review via the write_review endpoint."""
        resp = self.client.post(
            reverse('cart:write_review', args=[self.order.order_id, self.book1.book_id]),
            {'title': 'Great Read', 'content': 'Very enjoyable story.', 'rating': '4'}
        )
        self.assertEqual(resp.status_code, 302)

        rating = Rating.objects.get(customer=self.customer, book=self.book1)
        self.assertEqual(rating.score, 4)

        review = Review.objects.get(customer=self.customer, book=self.book1)
        self.assertEqual(review.title, 'Great Read')
        self.assertEqual(review.content, 'Very enjoyable story.')
