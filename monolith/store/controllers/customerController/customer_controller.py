"""
Customer controller - handles registration, login, logout, profile.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from store.controllers.customerController.forms import CustomerRegistrationForm, CustomerLoginForm
from store.models.customer.customer import Customer


class RegisterView(View):
    """Handle customer registration."""

    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('books:catalog')
        return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle customer login."""
    if request.method == 'POST':
        email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'books:catalog')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    form = CustomerLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Handle customer logout."""
    logout(request)
    return redirect('customer:login')


@login_required
def profile_view(request):
    """Display customer profile."""
    customer = request.user
    return render(request, 'accounts/profile.html', {'customer': customer})
