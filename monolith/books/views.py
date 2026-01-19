from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book


class BookCatalogView(LoginRequiredMixin, ListView):
    """View for displaying the book catalog."""
    
    model = Book
    template_name = 'books/catalog.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Book.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(author__icontains=search)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class BookDetailView(LoginRequiredMixin, DetailView):
    """View for displaying book details."""
    
    model = Book
    template_name = 'books/detail.html'
    context_object_name = 'book'


@login_required
def book_list_api(request):
    """API endpoint for listing books."""
    from django.http import JsonResponse
    
    books = Book.objects.all().values('id', 'title', 'author', 'price', 'stock')
    return JsonResponse({'books': list(books)})
