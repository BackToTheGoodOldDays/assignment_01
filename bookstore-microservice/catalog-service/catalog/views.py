from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Category, Author, Publisher
from .serializers import CategorySerializer, AuthorSerializer, PublisherSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    @action(detail=False, methods=['get'])
    def active(self, request):
        cats = Category.objects.filter(is_active=True)
        return Response(CategorySerializer(cats, many=True).data)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'bio']


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=False, methods=['get'])
    def active(self, request):
        pubs = Publisher.objects.filter(is_active=True)
        return Response(PublisherSerializer(pubs, many=True).data)
