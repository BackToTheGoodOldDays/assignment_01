#!/usr/bin/env python3
"""
seed_data.py - Insert sample data into all BookStore microservices.

Run AFTER migrations:
    python run_local.py migrate
    python seed_data.py

All services must be running (python run_local.py) OR MySQL must be accessible.
This script calls each service's REST API to insert sample data.
"""

import requests
import json
import sys
import time

# Fix Windows console encoding to support Unicode
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# ── Configuration ──────────────────────────────────────────────────────────────
BASE_URLS = {
    "staff":      "http://localhost:8001",
    "manager":    "http://localhost:8002",
    "customer":   "http://localhost:8003",
    "catalog":    "http://localhost:8004",
    "book":       "http://localhost:8005",
    "cart":       "http://localhost:8006",
    "order":      "http://localhost:8007",
    "ship":       "http://localhost:8008",
    "pay":        "http://localhost:8009",
    "comment":    "http://localhost:8010",
    "recommender": "http://localhost:8011",
}

TIMEOUT = 5

# ── Colors ─────────────────────────────────────────────────────────────────────
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = BLUE = CYAN = RESET = ""


def api(service, method, path, data=None, params=None, token=None):
    """Make an API call to a service."""
    url = BASE_URLS[service] + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            r = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        elif method == "PUT":
            r = requests.put(url, json=data, headers=headers, timeout=TIMEOUT)
        else:
            return None, 0
        return r.json() if r.content else {}, r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Connection refused - is the service running?"}, 503
    except Exception as e:
        return {"error": str(e)}, 500


def ok(msg, data=None):
    print(f"  {GREEN}✅  {msg}{RESET}")
    if data and isinstance(data, dict) and "error" not in data:
        pass
    return data


def fail(msg, data=None):
    print(f"  {RED}❌  {msg}{RESET}")
    if data:
        print(f"     {data}")


def section(title):
    print(f"\n{CYAN}{'─'*60}{RESET}")
    print(f"{CYAN}  {title}{RESET}")
    print(f"{CYAN}{'─'*60}{RESET}")


def check_service(service, path="/api/"):
    try:
        r = requests.get(BASE_URLS[service] + path, timeout=3)
        return r.status_code < 500
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  SEED FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def seed_staff():
    section("Staff Service - Creating Staff Accounts")

    staff_accounts = [
        {"username": "admin_staff", "name": "Admin User", "email": "admin@bookstore.com",
         "password": "Admin123!", "role": "admin"},
        {"username": "inventory_john", "name": "John Smith", "email": "john@bookstore.com",
         "password": "Staff123!", "role": "staff"},
        {"username": "inventory_jane", "name": "Jane Doe", "email": "jane@bookstore.com",
         "password": "Staff123!", "role": "staff"},
    ]

    created_staff = []
    for staff in staff_accounts:
        data, status = api("staff", "POST", "/api/staff/", staff)
        if status in (200, 201):
            ok(f"Created staff: {staff['username']} (role: {staff['role']})", data)
            created_staff.append(data)
        else:
            fail(f"Failed to create staff {staff['username']}: {data}")

    # Test login
    login_data, status = api("staff", "POST", "/api/staff/login/",
                             {"username": "admin_staff", "password": "Admin123!"})
    if status == 200:
        ok("Staff login test passed")
        return login_data.get("token"), created_staff
    fail("Staff login failed", login_data)
    return None, created_staff


def seed_managers():
    section("Manager Service - Creating Manager Accounts")

    managers = [
        {"username": "super_manager", "name": "Alice Manager", "email": "alice@bookstore.com",
         "password": "Manager123!"},
        {"username": "ops_manager", "name": "Bob Operations", "email": "bob@bookstore.com",
         "password": "Manager123!"},
    ]

    for mgr in managers:
        data, status = api("manager", "POST", "/api/managers/", mgr)
        if status in (200, 201):
            ok(f"Created manager: {mgr['username']}")
        else:
            fail(f"Failed to create manager {mgr['username']}: {data}")

    # Test login
    login_data, status = api("manager", "POST", "/api/managers/login/",
                             {"username": "super_manager", "password": "Manager123!"})
    if status == 200:
        ok("Manager login test passed")
        return login_data.get("token")
    fail("Manager login failed", login_data)
    return None


def seed_catalog():
    section("Catalog Service - Categories, Authors, Publishers")

    # Categories
    categories_data = [
        {"name": "Fiction", "description": "Fictional literature and novels"},
        {"name": "Non-Fiction", "description": "Factual books and real-world stories"},
        {"name": "Science Fiction", "description": "Speculative and futuristic fiction"},
        {"name": "Mystery & Thriller", "description": "Suspense and detective stories"},
        {"name": "Romance", "description": "Romantic fiction and love stories"},
        {"name": "Self-Help", "description": "Personal development and motivation"},
        {"name": "Technology", "description": "Programming, software, and tech books"},
        {"name": "History", "description": "Historical accounts and biographies"},
        {"name": "Children", "description": "Books for young readers"},
        {"name": "Business", "description": "Business, management, and economics"},
    ]

    category_ids = {}
    for cat in categories_data:
        data, status = api("catalog", "POST", "/api/categories/", cat)
        if status in (200, 201):
            ok(f"Category: {cat['name']}")
            category_ids[cat["name"]] = data.get("category_id")
        else:
            fail(f"Failed category {cat['name']}: {data}")

    # Authors
    authors_data = [
        {"name": "George Orwell", "bio": "English novelist, essayist and critic"},
        {"name": "J.K. Rowling", "bio": "British author of Harry Potter series"},
        {"name": "Frank Herbert", "bio": "Author of the Dune science fiction series"},
        {"name": "Agatha Christie", "bio": "English crime fiction writer"},
        {"name": "Stephen King", "bio": "American author of horror and suspense"},
        {"name": "Paulo Coelho", "bio": "Brazilian lyricist and novelist"},
        {"name": "Yuval Noah Harari", "bio": "Israeli public intellectual and historian"},
        {"name": "Robert Martin", "bio": "Software engineer and author of Clean Code"},
        {"name": "Eric Ries", "bio": "Author of The Lean Startup"},
        {"name": "Dale Carnegie", "bio": "American writer and lecturer"},
    ]

    author_ids = {}
    for author in authors_data:
        data, status = api("catalog", "POST", "/api/authors/", author)
        if status in (200, 201):
            ok(f"Author: {author['name']}")
            author_ids[author["name"]] = data.get("author_id")
        else:
            fail(f"Failed author {author['name']}: {data}")

    # Publishers
    publishers_data = [
        {"name": "Penguin Books", "email": "info@penguin.com", "website": "https://www.penguin.com"},
        {"name": "HarperCollins", "email": "info@harpercollins.com"},
        {"name": "Bloomsbury", "email": "info@bloomsbury.com"},
        {"name": "Secker & Warburg", "email": "info@seckerwarbug.com"},
        {"name": "O'Reilly Media", "email": "info@oreilly.com", "website": "https://www.oreilly.com"},
    ]

    publisher_ids = {}
    for pub in publishers_data:
        data, status = api("catalog", "POST", "/api/publishers/", pub)
        if status in (200, 201):
            ok(f"Publisher: {pub['name']}")
            publisher_ids[pub["name"]] = data.get("publisher_id")
        else:
            fail(f"Failed publisher {pub['name']}: {data}")

    return category_ids, author_ids, publisher_ids


def seed_books(category_ids, author_ids, publisher_ids):
    section("Book Service - Book Statuses & Books")

    # Create book statuses
    statuses = [
        {"status_name": "Available", "description": "Book is available for purchase"},
        {"status_name": "Out of Stock", "description": "Temporarily out of stock"},
        {"status_name": "Discontinued", "description": "No longer available"},
        {"status_name": "Pre-Order", "description": "Available for pre-order"},
    ]

    status_ids = {}
    for s in statuses:
        data, code = api("book", "POST", "/api/statuses/", s)
        if code in (200, 201):
            ok(f"Book status: {s['status_name']}")
            status_ids[s["status_name"]] = data.get("status_id")
        else:
            fail(f"Failed status {s['status_name']}: {data}")

    available_id = status_ids.get("Available", 1)

    # Create books
    books_data = [
        {
            "title": "1984",
            "isbn": "978-0-452-28423-4",
            "price": "12.99",
            "author_id": author_ids.get("George Orwell", 1),
            "category_id": category_ids.get("Fiction", 1),
            "publisher_id": publisher_ids.get("Secker & Warburg", 1),
            "status": available_id,
            "language": "English",
            "pages": 368,
            "description": "A dystopian social science fiction novel set in totalitarian Oceania.",
            "publication_year": 1949,
            "initial_stock": 150,
        },
        {
            "title": "Harry Potter and the Philosopher's Stone",
            "isbn": "978-0-7475-3269-9",
            "price": "14.99",
            "author_id": author_ids.get("J.K. Rowling", 2),
            "category_id": category_ids.get("Fiction", 1),
            "publisher_id": publisher_ids.get("Bloomsbury", 3),
            "status": available_id,
            "language": "English",
            "pages": 309,
            "description": "The beginning of Harry Potter's magical journey at Hogwarts.",
            "publication_year": 1997,
            "initial_stock": 200,
        },
        {
            "title": "Dune",
            "isbn": "978-0-441-17271-9",
            "price": "15.99",
            "author_id": author_ids.get("Frank Herbert", 3),
            "category_id": category_ids.get("Science Fiction", 3),
            "publisher_id": publisher_ids.get("Penguin Books", 1),
            "status": available_id,
            "language": "English",
            "pages": 688,
            "description": "An epic science fiction novel set in a distant future society.",
            "publication_year": 1965,
            "initial_stock": 100,
        },
        {
            "title": "Murder on the Orient Express",
            "isbn": "978-0-00-713800-5",
            "price": "11.99",
            "author_id": author_ids.get("Agatha Christie", 4),
            "category_id": category_ids.get("Mystery & Thriller", 4),
            "publisher_id": publisher_ids.get("HarperCollins", 2),
            "status": available_id,
            "language": "English",
            "pages": 256,
            "description": "Hercule Poirot investigates a murder on the famous Orient Express.",
            "publication_year": 1934,
            "initial_stock": 120,
        },
        {
            "title": "The Shining",
            "isbn": "978-0-385-12167-5",
            "price": "13.99",
            "author_id": author_ids.get("Stephen King", 5),
            "category_id": category_ids.get("Mystery & Thriller", 4),
            "publisher_id": publisher_ids.get("Penguin Books", 1),
            "status": available_id,
            "language": "English",
            "pages": 447,
            "description": "A horror novel about a family's winter caretaking at the Overlook Hotel.",
            "publication_year": 1977,
            "initial_stock": 80,
        },
        {
            "title": "The Alchemist",
            "isbn": "978-0-06-231500-7",
            "price": "10.99",
            "author_id": author_ids.get("Paulo Coelho", 6),
            "category_id": category_ids.get("Fiction", 1),
            "publisher_id": publisher_ids.get("HarperCollins", 2),
            "status": available_id,
            "language": "English",
            "pages": 197,
            "description": "A philosophical novel about following your dreams.",
            "publication_year": 1988,
            "initial_stock": 175,
        },
        {
            "title": "Sapiens: A Brief History of Humankind",
            "isbn": "978-0-06-231609-7",
            "price": "16.99",
            "author_id": author_ids.get("Yuval Noah Harari", 7),
            "category_id": category_ids.get("Non-Fiction", 2),
            "publisher_id": publisher_ids.get("HarperCollins", 2),
            "status": available_id,
            "language": "English",
            "pages": 443,
            "description": "A survey of the history of Homo sapiens from evolution to modern day.",
            "publication_year": 2011,
            "initial_stock": 130,
        },
        {
            "title": "Clean Code",
            "isbn": "978-0-13-235088-4",
            "price": "39.99",
            "author_id": author_ids.get("Robert Martin", 8),
            "category_id": category_ids.get("Technology", 7),
            "publisher_id": publisher_ids.get("O'Reilly Media", 5),
            "status": available_id,
            "language": "English",
            "pages": 464,
            "description": "A handbook of agile software craftsmanship.",
            "publication_year": 2008,
            "initial_stock": 90,
        },
        {
            "title": "The Lean Startup",
            "isbn": "978-0-30-788791-7",
            "price": "18.99",
            "author_id": author_ids.get("Eric Ries", 9),
            "category_id": category_ids.get("Business", 10),
            "publisher_id": publisher_ids.get("Penguin Books", 1),
            "status": available_id,
            "language": "English",
            "pages": 336,
            "description": "How today's entrepreneurs use continuous innovation to create businesses.",
            "publication_year": 2011,
            "initial_stock": 110,
        },
        {
            "title": "How to Win Friends and Influence People",
            "isbn": "978-0-67-142517-3",
            "price": "9.99",
            "author_id": author_ids.get("Dale Carnegie", 10),
            "category_id": category_ids.get("Self-Help", 6),
            "publisher_id": publisher_ids.get("Penguin Books", 1),
            "status": available_id,
            "language": "English",
            "pages": 288,
            "description": "A classic self-help book on human relations and communication.",
            "publication_year": 1936,
            "initial_stock": 200,
        },
    ]

    book_ids = []
    for book in books_data:
        data, status = api("book", "POST", "/api/books/", book)
        if status in (200, 201):
            ok(f"Book: {book['title']} (stock: {book['initial_stock']})")
            book_ids.append(data.get("book_id"))
        else:
            fail(f"Failed book {book['title']}: {data}")

    return book_ids


def seed_shipping_and_payment():
    section("Ship Service - Shipping Methods")

    methods = [
        {"name": "Standard Shipping", "description": "Delivery in 5-7 business days",
         "fee": "3.99", "estimated_days": 6},
        {"name": "Express Shipping", "description": "Delivery in 2-3 business days",
         "fee": "9.99", "estimated_days": 2},
        {"name": "Overnight Shipping", "description": "Next business day delivery",
         "fee": "24.99", "estimated_days": 1},
        {"name": "Free Shipping", "description": "Free delivery for orders over $50",
         "fee": "0.00", "estimated_days": 7},
    ]

    method_ids = []
    for method in methods:
        data, status = api("ship", "POST", "/api/shipping-methods/", method)
        if status in (200, 201):
            ok(f"Shipping: {method['name']} (${method['fee']})")
            method_ids.append(data.get("method_id"))
        else:
            fail(f"Failed shipping method {method['name']}: {data}")

    section("Pay Service - Payment Methods")

    pay_methods = [
        {"name": "Credit Card", "code": "credit_card",
         "description": "Pay with Visa, Mastercard, etc."},
        {"name": "Debit Card", "code": "debit_card",
         "description": "Pay with your bank debit card"},
        {"name": "PayPal", "code": "paypal",
         "description": "Pay securely with PayPal"},
        {"name": "Cash on Delivery", "code": "cod",
         "description": "Pay when your order arrives"},
        {"name": "Bank Transfer", "code": "bank_transfer",
         "description": "Direct bank transfer payment"},
    ]

    pay_ids = []
    for method in pay_methods:
        data, status = api("pay", "POST", "/api/payment-methods/", method)
        if status in (200, 201):
            ok(f"Payment: {method['name']} ({method['code']})")
            pay_ids.append(data.get("method_id"))
        else:
            fail(f"Failed payment method {method['name']}: {data}")

    return method_ids, pay_ids


def seed_customers():
    section("Customer Service - Creating Customer Accounts")

    customers = [
        {"name": "Alice Johnson", "email": "alice@example.com",
         "phone": "+1-555-0001", "password": "Customer123!"},
        {"name": "Bob Williams", "email": "bob@example.com",
         "phone": "+1-555-0002", "password": "Customer123!"},
        {"name": "Carol Davis", "email": "carol@example.com",
         "phone": "+1-555-0003", "password": "Customer123!"},
        {"name": "David Wilson", "email": "david@example.com",
         "phone": "+1-555-0004", "password": "Customer123!"},
        {"name": "Emma Brown", "email": "emma@example.com",
         "phone": "+1-555-0005", "password": "Customer123!"},
    ]

    customer_data = []
    for cust in customers:
        data, status = api("customer", "POST", "/api/customers/register/", cust)
        if status in (200, 201):
            cust_obj = data.get("customer", data)
            token = data.get("token")
            ok(f"Customer: {cust['name']} ({cust['email']})")
            customer_data.append({"customer": cust_obj, "token": token})
        else:
            fail(f"Failed customer {cust['name']}: {data}")

    return customer_data


def seed_carts(customer_data, book_ids):
    section("Cart Service - Adding Items to Carts")

    if not customer_data or not book_ids:
        print(f"  {YELLOW}⚠  Skipping cart seeding (no customers or books){RESET}")
        return []

    cart_ids = []
    for i, cust_info in enumerate(customer_data[:3]):  # Seed for first 3 customers
        cust = cust_info["customer"]
        customer_id = cust.get("customer_id")
        if not customer_id:
            continue

        # Get active cart
        cart_data, status = api("cart", "GET", f"/api/carts/active-cart/?customer_id={customer_id}")
        if status != 200:
            fail(f"No active cart for customer {customer_id}: {cart_data}")
            continue

        cart_id = cart_data.get("cart_id")
        if not cart_id:
            continue

        cart_ids.append(cart_id)

        # Add 2-3 books to the cart
        items_to_add = book_ids[:i+2]
        for book_id in items_to_add:
            if not book_id:
                continue
            item_data, item_status = api("cart", "POST", f"/api/carts/{cart_id}/add-item/",
                                         {"book_id": book_id, "quantity": 1})
            if item_status in (200, 201):
                ok(f"  Added book #{book_id} to cart #{cart_id}")
            else:
                fail(f"  Failed to add book #{book_id} to cart #{cart_id}: {item_data}")

    return cart_ids


def seed_orders(customer_data, cart_ids, shipping_method_ids, payment_method_ids):
    section("Order Service - Creating Sample Orders")

    if not customer_data or not cart_ids:
        print(f"  {YELLOW}⚠  Skipping order seeding{RESET}")
        return

    shipping_id = shipping_method_ids[0] if shipping_method_ids else 1
    payment_id = payment_method_ids[0] if payment_method_ids else 1

    orders_created = 0
    for i, (cust_info, cart_id) in enumerate(zip(customer_data[:2], cart_ids[:2])):
        cust = cust_info["customer"]
        customer_id = cust.get("customer_id")
        if not customer_id or not cart_id:
            continue

        order_payload = {
            "customer_id": customer_id,
            "cart_id": cart_id,
            "shipping_address": f"123 Main St, City {i+1}, State, 10001",
            "shipping_method_id": shipping_id,
            "payment_method_id": payment_id,
            "notes": "Sample order from seed data",
        }

        data, status = api("order", "POST", "/api/orders/", order_payload)
        if status in (200, 201):
            ok(f"Order created: {data.get('order_number')} for customer {customer_id}")
            orders_created += 1
        else:
            fail(f"Failed to create order for customer {customer_id}: {data}")

    if orders_created:
        print(f"  {GREEN}Created {orders_created} sample orders{RESET}")


def seed_reviews(customer_data, book_ids):
    section("Comment-Rate Service - Adding Reviews")

    if not customer_data or not book_ids:
        print(f"  {YELLOW}⚠  Skipping reviews{RESET}")
        return

    reviews = [
        (1, book_ids[0], 5, "Brilliant!", "A masterpiece of dystopian literature."),
        (2, book_ids[0], 5, "Classic", "Every person should read this book."),
        (1, book_ids[1], 5, "Magical", "The beginning of an incredible series."),
        (3, book_ids[2], 4, "Epic Sci-Fi", "Complex but rewarding. Dune is a true epic."),
        (2, book_ids[3], 5, "Perfect Mystery", "Christie at her best!"),
        (4, book_ids[6], 5, "Eye-opening", "Changed how I see human history."),
        (3, book_ids[7], 5, "Must Read", "Essential for any software developer."),
    ]

    for cust_idx, book_id, rating, title, content in reviews:
        if cust_idx > len(customer_data) or not book_id:
            continue
        cust = customer_data[cust_idx - 1]["customer"]
        customer_id = cust.get("customer_id")

        review_data = {
            "book_id": book_id,
            "customer_id": customer_id,
            "rating": rating,
            "title": title,
            "content": content,
        }
        data, status = api("comment", "POST", "/api/reviews/", review_data)
        if status in (200, 201):
            ok(f"Review: {title} (⭐{rating}) for book #{book_id}")
        else:
            fail(f"Failed review for book #{book_id}: {data}")


def seed_interactions(customer_data, book_ids):
    section("Recommender Service - Logging Interactions")

    if not customer_data or not book_ids:
        print(f"  {YELLOW}⚠  Skipping interaction seeding{RESET}")
        return

    interactions = []
    for i, cust_info in enumerate(customer_data[:3]):
        cust = cust_info["customer"]
        cid = cust.get("customer_id")
        if not cid:
            continue
        # Each customer views a few books
        for book_id in book_ids[i:i+4]:
            if book_id:
                interactions.append({
                    "customer_id": cid,
                    "book_id": book_id,
                    "interaction_type": "view",
                })
        # Purchase interaction for ordered books
        if book_ids:
            interactions.append({
                "customer_id": cid,
                "book_id": book_ids[i % len(book_ids)],
                "interaction_type": "purchase",
            })

    for inter in interactions:
        data, status = api("recommender", "POST", "/api/interactions/", inter)
        if status in (200, 201):
            ok(f"Interaction: customer #{inter['customer_id']} {inter['interaction_type']} book #{inter['book_id']}")
        else:
            fail(f"Failed interaction: {data}")


def check_all_services():
    """Verify all services are reachable."""
    section("Checking Service Availability")
    all_ok = True
    service_checks = {
        "staff": "/api/staff/",
        "manager": "/api/managers/",
        "customer": "/api/customers/",
        "catalog": "/api/categories/",
        "book": "/api/books/",
        "cart": "/api/carts/active-cart/?customer_id=0",
        "order": "/api/orders/",
        "ship": "/api/shipping-methods/",
        "pay": "/api/payment-methods/",
        "comment": "/api/reviews/",
        "recommender": "/api/trending/",
    }
    for service, path in service_checks.items():
        try:
            r = requests.get(BASE_URLS[service] + path, timeout=3)
            if r.status_code < 500:
                print(f"  {GREEN}✅  {service:<25} {BASE_URLS[service]}{RESET}")
            else:
                print(f"  {RED}❌  {service:<25} HTTP {r.status_code}{RESET}")
                all_ok = False
        except Exception as e:
            print(f"  {RED}❌  {service:<25} {e}{RESET}")
            all_ok = False
    return all_ok


def print_summary():
    """Print login credentials summary."""
    print(f"\n{CYAN}{'═'*60}{RESET}")
    print(f"{CYAN}  SEED DATA COMPLETE - Login Credentials{RESET}")
    print(f"{CYAN}{'═'*60}{RESET}")
    print(f"""
  {YELLOW}Customer Accounts:{RESET}
    alice@example.com  / Customer123!
    bob@example.com    / Customer123!
    carol@example.com  / Customer123!
    david@example.com  / Customer123!
    emma@example.com   / Customer123!

  {YELLOW}Staff Accounts:{RESET}
    admin_staff        / Admin123!     (role: admin)
    inventory_john     / Staff123!     (role: staff)
    inventory_jane     / Staff123!     (role: staff)

  {YELLOW}Manager Accounts:{RESET}
    super_manager      / Manager123!
    ops_manager        / Manager123!

  {YELLOW}Access Points:{RESET}
    Web UI:            http://localhost:8000
    Staff Login:       http://localhost:8000/staff/login/
    Manager Login:     http://localhost:8000/manager/login/
    API Gateway:       http://localhost:8000/api/
""")
    print(f"{CYAN}{'═'*60}{RESET}\n")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════╗
║     BookStore Microservices - Seed Data Script       ║
╚══════════════════════════════════════════════════════╝{RESET}

Make sure all services are running before proceeding.
""")

    # Check services
    if "--skip-check" not in sys.argv:
        services_ok = check_all_services()
        if not services_ok:
            print(f"\n{YELLOW}⚠  Some services are not reachable.{RESET}")
            resp = input("  Continue anyway? [y/N] ").strip().lower()
            if resp != "y":
                print("Aborting.")
                sys.exit(1)

    # Run seeding
    staff_token, staff_list = seed_staff()
    manager_token = seed_managers()
    category_ids, author_ids, publisher_ids = seed_catalog()
    book_ids = seed_books(category_ids, author_ids, publisher_ids)
    shipping_ids, payment_ids = seed_shipping_and_payment()
    customer_data = seed_customers()

    # Small delay to ensure carts are created
    time.sleep(1)

    cart_ids = seed_carts(customer_data, book_ids)
    seed_orders(customer_data, cart_ids, shipping_ids, payment_ids)
    seed_reviews(customer_data, book_ids)
    seed_interactions(customer_data, book_ids)

    print_summary()


if __name__ == "__main__":
    main()
