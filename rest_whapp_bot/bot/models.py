from django.db import models
import datetime as dt

# Create your models here.
class Customer(models.Model):
    phonenumber = models.CharField(unique=True, max_length=15)
    start = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    phonenumber = models.BigIntegerField(default=0)
    message = models.CharField(max_length=120)
    order_date = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    index = models.IntegerField(unique=True, default=None)
    product = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    stock = models.IntegerField()
    start_date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product_list = models.JSONField()
    cost = models.DecimalField(decimal_places=2, max_digits=10)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    date = models.DateTimeField(auto_now=True)
    cart_closed = models.BooleanField(default=False)