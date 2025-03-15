from rest_framework import serializers
from .models import Category, Product, ProductImage
from accounts.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product additional images"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products list view"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'price', 'image', 'category', 'category_name',
            'seller', 'seller_name', 'in_stock', 'quantity', 'created_at'
        ]
        read_only_fields = ['seller']
    
    def create(self, validated_data):
        """Set the seller to the current user"""
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail view with additional data"""
    category = CategorySerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'title', 'description', 'price', 'category',
            'image', 'additional_images', 'in_stock', 'quantity', 
            'created_at', 'updated_at'
        ]