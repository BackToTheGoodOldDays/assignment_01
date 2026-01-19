from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomerRegistrationForm, CustomerLoginForm
from .models import Customer


class RegisterView(CreateView):
    """View for customer registration."""
    
    model = Customer
    form_class = CustomerRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login.')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('books:catalog')
        return super().dispatch(request, *args, **kwargs)


def login_view(request):
    """View for customer login."""
    if request.user.is_authenticated:
        return redirect('books:catalog')
    
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.name}!')
            next_url = request.GET.get('next', 'books:catalog')
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
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """View for customer profile."""
    return render(request, 'accounts/profile.html', {'customer': request.user})
