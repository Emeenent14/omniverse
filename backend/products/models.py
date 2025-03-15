from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    """Product model"""
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='product_images/')
    in_stock = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class ProductImage(models.Model):
    """Additional product images"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='product_images/')
    
    def __str__(self):
        return f"Image for {self.product.title}"