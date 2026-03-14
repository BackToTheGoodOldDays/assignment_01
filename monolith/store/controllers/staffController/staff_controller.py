"""
Staff controller - handles staff login, inventory management, dashboard.
"""
import json
import csv
import io
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from store.models.staff.staff import Staff, InventoryLog
from store.models.book.book import Book, Author, Category, Publisher, BookInventory
from store.models.order.order import Order, OrderStatus


def staff_login_required(view_func):
    """Decorator to require staff login."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        staff_id = request.session.get('staff_id')
        if not staff_id:
            return redirect('staff:login')
        try:
            request.staff = Staff.objects.get(staff_id=staff_id, is_active=True)
        except Staff.DoesNotExist:
            del request.session['staff_id']
            return redirect('staff:login')
        return view_func(request, *args, **kwargs)
    return _wrapped


def staff_login(request):
    """Handle staff login."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        try:
            staff = Staff.objects.get(email=email, is_active=True)
            if staff.check_password(password):
                request.session['staff_id'] = staff.staff_id
                staff.last_login = timezone.now()
                staff.save(update_fields=['last_login'])
                return redirect('staff:dashboard')
            else:
                messages.error(request, 'Invalid password.')
        except Staff.DoesNotExist:
            messages.error(request, 'Staff account not found.')
    return render(request, 'staff/login.html')


def staff_logout(request):
    """Handle staff logout."""
    if 'staff_id' in request.session:
        del request.session['staff_id']
    return redirect('staff:login')


@staff_login_required
def dashboard(request):
    """Display staff dashboard."""
    stats = {
        'total_books': Book.objects.count(),
        'low_stock': BookInventory.objects.filter(quantity__lte=5).count(),
        'pending_orders': Order.objects.filter(status__name='Pending').count(),
        'total_customers': 0,
    }

    from store.models.customer.customer import Customer
    stats['total_customers'] = Customer.objects.count()

    recent_orders = Order.objects.select_related('customer', 'status').order_by('-order_date')[:10]
    low_stock_books = Book.objects.filter(
        inventory__quantity__lte=5
    ).annotate(stock_quantity=Sum('inventory__quantity')).order_by('inventory__quantity')[:10]

    return render(request, 'staff/dashboard.html', {
        'staff': request.staff,
        'stats': stats,
        'recent_orders': recent_orders,
        'low_stock_books': low_stock_books,
    })


@staff_login_required
def inventory_list(request):
    """Display inventory list."""
    books = Book.objects.select_related('author', 'category', 'inventory').annotate(
        stock_quantity=Sum('inventory__quantity')
    )

    search = request.GET.get('search', '').strip()
    if search:
        books = books.filter(Q(title__icontains=search) | Q(isbn__icontains=search) | Q(author__name__icontains=search))

    filter_val = request.GET.get('filter')
    if filter_val == 'low_stock':
        books = books.filter(inventory__quantity__lte=5)
    elif filter_val == 'out_of_stock':
        books = books.filter(inventory__quantity=0)

    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(category_id=category_id)

    categories = Category.objects.all()

    paginator = Paginator(books, 20)
    page = request.GET.get('page')
    books = paginator.get_page(page)

    return render(request, 'staff/inventory_list.html', {
        'staff': request.staff,
        'books': books,
        'categories': categories,
        'is_paginated': books.has_other_pages(),
        'page_obj': books,
    })


@staff_login_required
def add_book(request):
    """Add a new book."""
    if request.method == 'POST':
        title = request.POST.get('title', '')
        isbn = request.POST.get('isbn', '')
        author_id = request.POST.get('author')
        category_id = request.POST.get('category')
        publisher_id = request.POST.get('publisher')
        price = request.POST.get('price', 0)
        stock = int(request.POST.get('stock_quantity', 0))
        description_text = request.POST.get('description', '')
        short_desc = request.POST.get('short_description', '')
        pub_date = request.POST.get('publication_date') or None
        image_url = request.POST.get('image_url', '')

        # Handle new author
        new_author_name = request.POST.get('new_author_name', '').strip()
        if new_author_name:
            author_obj, _ = Author.objects.get_or_create(name=new_author_name)
            author_id = author_obj.author_id

        book = Book.objects.create(
            title=title, isbn=isbn, price=price,
            author_id=author_id or None,
            category_id=category_id or None,
            publisher_id=publisher_id or None,
            publication_date=pub_date,
        )

        if description_text or short_desc:
            from store.models.book.book import BookDescription
            BookDescription.objects.create(
                book=book, content=description_text, short_description=short_desc,
            )

        if stock > 0:
            BookInventory.objects.create(book=book, quantity=stock)

        if image_url:
            from store.models.book.book import BookImage
            BookImage.objects.create(book=book, url=image_url, is_primary=True)

        InventoryLog.objects.create(
            staff=request.staff, book=book, action='add',
            quantity=stock, previous_quantity=0, new_quantity=stock,
            notes=f'New book added: {title}',
        )
        messages.success(request, f'Book "{title}" added successfully!')
        return redirect('staff:inventory_list')

    authors = Author.objects.all()
    categories = Category.objects.all()
    publishers = Publisher.objects.all()

    return render(request, 'staff/add_book.html', {
        'staff': request.staff,
        'authors': authors,
        'categories': categories,
        'publishers': publishers,
    })


@staff_login_required
def import_stock(request):
    """Import stock for a book."""
    if request.method == 'POST':
        import_type = request.POST.get('import_type', 'single')
        book_id = request.POST.get('book')
        quantity = int(request.POST.get('quantity', 0))
        notes = request.POST.get('notes', '')

        if book_id and quantity > 0:
            book = get_object_or_404(Book, book_id=book_id)
            inventory, _ = BookInventory.objects.get_or_create(book=book, defaults={'quantity': 0})
            previous = inventory.quantity
            inventory.add_stock(quantity)

            InventoryLog.objects.create(
                staff=request.staff, book=book, action='import',
                quantity=quantity, previous_quantity=previous,
                new_quantity=inventory.quantity, notes=notes,
            )
            messages.success(request, f'Imported {quantity} units of "{book.title}".')
        else:
            messages.error(request, 'Please select a book and enter a valid quantity.')
        return redirect('staff:import_stock')

    books = Book.objects.select_related('inventory').annotate(
        stock_quantity=Sum('inventory__quantity')
    )
    recent_logs = InventoryLog.objects.select_related('book', 'staff').order_by('-created_at')[:20]

    return render(request, 'staff/import_stock.html', {
        'staff': request.staff,
        'books': books,
        'recent_logs': recent_logs,
    })


@staff_login_required
def bulk_import(request):
    """Bulk import stock from CSV/JSON data."""
    if request.method == 'POST':
        bulk_data = request.POST.get('bulk_data', '')
        notes = request.POST.get('bulk_notes', '')
        count = 0

        for line in bulk_data.strip().split('\n'):
            parts = line.strip().split(',')
            if len(parts) >= 2:
                book_id_or_isbn = parts[0].strip()
                qty = int(parts[1].strip())

                book = Book.objects.filter(
                    Q(book_id=book_id_or_isbn) | Q(isbn=book_id_or_isbn)
                ).first()

                if book and qty > 0:
                    inventory, _ = BookInventory.objects.get_or_create(book=book, defaults={'quantity': 0})
                    previous = inventory.quantity
                    inventory.add_stock(qty)
                    InventoryLog.objects.create(
                        staff=request.staff, book=book, action='import',
                        quantity=qty, previous_quantity=previous,
                        new_quantity=inventory.quantity, notes=f'Bulk import: {notes}',
                    )
                    count += 1

        messages.success(request, f'Bulk import complete: {count} items updated.')
        return redirect('staff:import_stock')
    return redirect('staff:import_stock')


@staff_login_required
def inventory_logs(request):
    """Display inventory logs."""
    logs = InventoryLog.objects.select_related('book', 'staff').all()

    search = request.GET.get('search', '').strip()
    if search:
        logs = logs.filter(Q(book__title__icontains=search) | Q(book__isbn__icontains=search))

    log_type = request.GET.get('type')
    if log_type:
        logs = logs.filter(action=log_type)

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if from_date:
        logs = logs.filter(created_at__date__gte=from_date)
    if to_date:
        logs = logs.filter(created_at__date__lte=to_date)

    stats = {
        'total_import': logs.filter(action='import').aggregate(total=Sum('quantity'))['total'] or 0,
        'total_sale': logs.filter(action='reduce').aggregate(total=Sum('quantity'))['total'] or 0,
        'total_adjust': logs.filter(action='adjust').aggregate(total=Sum('quantity'))['total'] or 0,
    }

    paginator = Paginator(logs, 20)
    page = request.GET.get('page')
    logs = paginator.get_page(page)

    return render(request, 'staff/inventory_logs.html', {
        'staff': request.staff,
        'logs': logs,
        'stats': stats,
        'is_paginated': logs.has_other_pages(),
        'page_obj': logs,
    })


@staff_login_required
def adjust_stock(request):
    """Adjust stock quantity for a book."""
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        new_quantity = int(request.POST.get('new_quantity', 0))
        reason = request.POST.get('reason', '')
        notes = request.POST.get('notes', '')

        book = get_object_or_404(Book, book_id=book_id)
        inventory, _ = BookInventory.objects.get_or_create(book=book, defaults={'quantity': 0})
        previous = inventory.quantity
        inventory.quantity = new_quantity
        inventory.save()

        InventoryLog.objects.create(
            staff=request.staff, book=book, action='adjust',
            quantity=new_quantity - previous, previous_quantity=previous,
            new_quantity=new_quantity, notes=f'{reason}: {notes}',
        )
        messages.success(request, f'Stock adjusted for "{book.title}".')

    return redirect('staff:inventory_list')


@staff_login_required
def import_stock_general(request):
    """General stock import page."""
    return redirect('staff:import_stock')


@staff_login_required
def adjust_stock_general(request):
    """General stock adjustment."""
    return redirect('staff:inventory_list')


# API endpoints

@staff_login_required
def api_inventory_status(request):
    """API: Get inventory status."""
    books = Book.objects.select_related('inventory').all()
    data = [{
        'id': b.book_id,
        'title': b.title,
        'stock': b.inventory.quantity if hasattr(b, 'inventory') and b.inventory else 0,
        'status': b.inventory.check_stock() if hasattr(b, 'inventory') and b.inventory else 'out_of_stock',
    } for b in books]
    return JsonResponse({'inventory': data})


@staff_login_required
def api_quick_import(request):
    """API: Quick import stock."""
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        quantity = int(request.POST.get('quantity', 0))
        notes = request.POST.get('notes', '')

        if book_id and quantity > 0:
            book = get_object_or_404(Book, book_id=book_id)
            inventory, _ = BookInventory.objects.get_or_create(book=book, defaults={'quantity': 0})
            previous = inventory.quantity
            inventory.add_stock(quantity)

            InventoryLog.objects.create(
                staff=request.staff, book=book, action='import',
                quantity=quantity, previous_quantity=previous,
                new_quantity=inventory.quantity, notes=notes,
            )
            messages.success(request, f'Quick import: {quantity} units of "{book.title}".')
        else:
            messages.error(request, 'Invalid book or quantity.')

    return redirect('staff:inventory_list')
