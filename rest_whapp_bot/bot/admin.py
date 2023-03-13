from django.contrib import admin
from .models import Customer, Order, Product, Cart

# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'phonenumber']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'phonenumber', 'message', 'order_date']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'index', 'product', 'price', 'stock', 'start_date', 'update']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'product_list', 'cost', 'product']