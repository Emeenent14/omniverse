from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from .models import CartItem
from .serializers import CartItemSerializer, CartSummarySerializer

class CartViewSet(viewsets.ModelViewSet):
    """
    API endpoint for cart operations
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return cart items for the current user
        """
        return CartItem.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get a summary of the cart (total items, total price)
        """
        queryset = self.get_queryset()
        
        # Calculate total items and price
        item_count = queryset.count()
        total_price = queryset.annotate(
            item_total=F('quantity') * F('product__price')
        ).aggregate(
            total=Coalesce(Sum('item_total'), 0, output_field=DecimalField())
        )['total']
        
        serializer = CartSummarySerializer({
            'item_count': item_count,
            'total_price': total_price
        })
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """
        Clear all items from the cart
        """
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def create(self, request, *args, **kwargs):
        """
        Override create to handle existing cart items
        """
        # Check if item already exists in cart
        product_id = request.data.get('product')
        if product_id:
            existing_item = CartItem.objects.filter(
                user=request.user, 
                product_id=product_id
            ).first()
            
            if existing_item:
                # Update quantity instead of creating new
                new_quantity = existing_item.quantity + int(request.data.get('quantity', 1))
                serializer = self.get_serializer(
                    existing_item, 
                    data={'quantity': new_quantity}, 
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
        
        # Continue with normal creation if no existing item
        return super().create(request, *args, **kwargs)