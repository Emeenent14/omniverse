from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class CartItem(models.Model):
    """
    Cart item model - represents a product in a user's cart
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure a user can't add the same product to their cart multiple times
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username}'s cart: {self.product.title} x{self.quantity}"
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.product.price * self.quantity