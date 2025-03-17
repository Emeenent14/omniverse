from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer, ProductSerializer, ProductDetailSerializer,
    ProductImageSerializer
)

class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a product to edit it
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the seller
        return obj.seller == request.user

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for listing and retrieving product categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on products
    """
    queryset = Product.objects.all().order_by('-created_at')
    permission_classes = [IsSellerOrReadOnly]
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action
        """
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsSellerOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Optionally filter products by category, search term, or user
        """
        queryset = Product.objects.all().order_by('-created_at')
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__id=category)
        
        # Filter by search term
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by user's products
        my_products = self.request.query_params.get('my_products', None)
        if my_products and self.request.user.is_authenticated:
            queryset = queryset.filter(seller=self.request.user)
            
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_image(self, request, pk=None):
        """
        Add additional images to a product
        """
        product = self.get_object()
        
        # Check if user is the seller
        if product.seller != request.user:
            return Response(
                {'detail': 'You do not have permission to add images to this product.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)