"""
Django views for Clean Architecture bookstore.
Views act as controllers/presenters connecting use cases to the web interface.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import CustomerRegistrationForm, CustomerLoginForm
from .models import CustomerModel, BookModel, CartModel, CartItemModel

# Import use cases and repositories
from usecases.customer_usecases import RegisterCustomerUseCase, AuthenticateCustomerUseCase
from usecases.book_usecases import GetAllBooksUseCase, GetBookByIdUseCase
from usecases.cart_usecases import (
    GetOrCreateCartUseCase, AddToCartUseCase, UpdateCartItemUseCase,
    RemoveFromCartUseCase, ClearCartUseCase, GetCartUseCase
)
from infrastructure.repositories.django_customer_repository import DjangoCustomerRepository
from infrastructure.repositories.django_book_repository import DjangoBookRepository
from infrastructure.repositories.django_cart_repository import DjangoCartRepository


# Initialize repositories
customer_repository = DjangoCustomerRepository()
book_repository = DjangoBookRepository()
cart_repository = DjangoCartRepository()


# ==================== Account Views ====================

class RegisterView(CreateView):
    """View for customer registration using Clean Architecture."""
    
    model = CustomerModel
    form_class = CustomerRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login.')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('catalog')
        return super().dispatch(request, *args, **kwargs)


def login_view(request):
    """View for customer login."""
    if request.user.is_authenticated:
        return redirect('catalog')
    
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.name}!')
            next_url = request.GET.get('next', 'catalog')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomerLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """View for customer logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    """View for customer profile."""
    return render(request, 'accounts/profile.html', {'customer': request.user})


# ==================== Book Views ====================

@login_required
def catalog_view(request):
    """View for displaying the book catalog using use case."""
    search = request.GET.get('search', '')
    
    # Use the GetAllBooksUseCase
    use_case = GetAllBooksUseCase(book_repository)
    books = use_case.execute(search if search else None)
    
    return render(request, 'books/catalog.html', {
        'books': books,
        'search': search
    })


@login_required
def book_detail_view(request, pk):
    """View for displaying book details using use case."""
    use_case = GetBookByIdUseCase(book_repository)
    book = use_case.execute(pk)
    
    if not book:
        messages.error(request, 'Book not found.')
        return redirect('catalog')
    
    return render(request, 'books/detail.html', {'book': book})


# ==================== Cart Views ====================

@login_required
def cart_view(request):
    """View for displaying the shopping cart using use case."""
    use_case = GetOrCreateCartUseCase(cart_repository)
    cart = use_case.execute(request.user.id)
    
    return render(request, 'cart/cart.html', {'cart': cart})


@login_required
@require_POST
def add_to_cart_view(request, book_id):
    """Add a book to the shopping cart using use case."""
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        use_case = AddToCartUseCase(cart_repository, book_repository)
        cart = use_case.execute(request.user.id, book_id, quantity)
        
        book = book_repository.find_by_id(book_id)
        messages.success(request, f'Added "{book.title}" to your cart.')
        
    except ValueError as e:
        messages.error(request, str(e))
    
    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        get_cart_use_case = GetCartUseCase(cart_repository)
        cart = get_cart_use_case.execute(request.user.id)
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_items if cart else 0
        })
    
    return redirect('cart')


@login_required
@require_POST
def update_cart_item_view(request, book_id):
    """Update quantity of a cart item using use case."""
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        use_case = UpdateCartItemUseCase(cart_repository, book_repository)
        use_case.execute(request.user.id, book_id, quantity)
        messages.success(request, 'Cart updated successfully.')
    except ValueError as e:
        messages.error(request, str(e))
    
    return redirect('cart')


@login_required
@require_POST
def remove_from_cart_view(request, book_id):
    """Remove an item from the shopping cart using use case."""
    try:
        use_case = RemoveFromCartUseCase(cart_repository)
        use_case.execute(request.user.id, book_id)
        messages.info(request, 'Item removed from cart.')
    except ValueError as e:
        messages.error(request, str(e))
    
    return redirect('cart')


@login_required
@require_POST
def clear_cart_view(request):
    """Clear all items from the shopping cart using use case."""
    try:
        use_case = ClearCartUseCase(cart_repository)
        use_case.execute(request.user.id)
        messages.info(request, 'Your cart has been cleared.')
    except ValueError as e:
        messages.error(request, str(e))
    
    return redirect('cart')


@login_required
def cart_api_view(request):
    """API endpoint for cart data."""
    use_case = GetOrCreateCartUseCase(cart_repository)
    cart = use_case.execute(request.user.id)
    
    items = [{
        'id': item.id,
        'book_id': item.book_id,
        'book_title': item.book_title,
        'book_author': item.book_author,
        'quantity': item.quantity,
        'price': float(item.book_price),
        'subtotal': float(item.subtotal)
    } for item in cart.items]
    
    return JsonResponse({
        'cart_id': cart.id,
        'items': items,
        'total_items': cart.total_items,
        'total_price': float(cart.total_price)
    })
