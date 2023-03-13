from rest_framework import serializers
from .models import Customer, Order, Cart

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phonenumber']
    
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer', 'phonenumber', 'message']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['customer', 'product_list', 'cost', 'product', 'cart_closed'] 