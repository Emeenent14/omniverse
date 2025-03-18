from rest_framework import serializers
from .models import CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    product_detail = ProductSerializer(source='product', read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'user', 'product', 'product_detail', 
            'quantity', 'total_price', 'added_at'
        ]
        read_only_fields = ['user', 'total_price']
    
    def validate(self, attrs):
        """Validate that quantity doesn't exceed available stock"""
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        
        if product and not product.in_stock:
            raise serializers.ValidationError(
                {"product": "This product is not in stock."}
            )
            
        if product and quantity and quantity > product.quantity:
            raise serializers.ValidationError(
                {"quantity": f"Only {product.quantity} units available."}
            )
            
        return attrs
    
    def create(self, validated_data):
        """Set the user to the current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class CartSummarySerializer(serializers.Serializer):
    """Serializer for cart summary data"""
    item_count = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
