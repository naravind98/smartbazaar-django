from django.contrib import admin
from .models import Cart, CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_available')

# Register your models here.
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)         # Note: Each model class should be registered separately

