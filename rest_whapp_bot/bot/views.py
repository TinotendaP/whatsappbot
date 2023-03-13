from django.shortcuts import render

# Create your views here.
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from twilio.twiml.messaging_response import MessagingResponse, Media, Message, Body
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, StreamingHttpResponse, FileResponse
import re, shelve, os.path
from twilio.rest import Client
import datetime as dt
from .models import Customer, Order, Cart, Product
from .serializers import CustomerSerializer, OrderSerializer, CartSerializer
from django.core.exceptions import ObjectDoesNotExist
import json
from PIL import Image

# Create your views here.
# This is a whatsapp bot by that it means this program will automatically reply to whatsapp 
# messages send to this bot's account.
# This program is set to work under agrostock to sell agricultural products.
# The code below is set so as to be able to reply to specific messages with specific responses which are hard coded below

class Time:

    def __init__(self, days, hours, minutes, seconds):
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def __sub__(self, other):

        self.hours = self.days*24
        other.hours = other.days*24
        
        if self.minutes<other.minutes:
            self.hours-=1
            self.minutes+=60

        if self.seconds<other.seconds:
            self.minutes-=1
            self.seconds+=60

        return(self.hours, self.minutes, self.seconds)

    def sum(self):
        self.hours = self.days*24
        self.minutes = self.hours*60
        self.seconds = self.minutes*60
        return self.seconds


class Index:
    @csrf_exempt
    # This is the function that will be the brain of the bot
    def index(request):
        resp=MessagingResponse()
        msg=resp.message()

        if request.method =='POST':
            incoming_message=request.POST['Body'].lower() 
            whatsapp_phonenumber=request.POST['From']


            # This is a regex pattern that exracts the phonenumber from the twilio reply
            digit = re.compile(r'\d+')
            digit_finder = digit.search(whatsapp_phonenumber)
            phonenumber = digit_finder.group(0)

            # We are checkng if the phonenumber is already in the database or if it's a new customer
            
            #customer_contact = Customer.objects.filter(phonenumber = phonenumber)
            #print(customer_contact[0].id)
            products = Product.objects.all()

            message=''
            for product in products:
                res = '{0}. {1} at ${2} per kg \n'.format(product.index, product.product, product.price)
                message+=res
            
            customer_contact = Customer.objects.filter(phonenumber = phonenumber)
            # We are trying to retrieve messages which will only work f the given phonenumber was 
            # already in the database else an error will occur hence the trial and error method

            messages = Order.objects.filter(customer_id = customer_contact[0].id)

            #messages = Order.objects.filter(customer_id = customer_contact[0].id)
            #print(messages)

            # trying to retreive the customers cart if any exists
            carts = Cart.objects.filter(customer_id = customer_contact[0].id).filter(cart_closed = False)
            if len(carts)>0:
                now = dt.datetime.now()
                cart_date = carts[len(carts)-1].date
                time_now = Time(now.day, now.hour, now.minute, now.second)
                time_cart = Time(cart_date.day, cart_date.hour, cart_date.minute, cart_date.second)
                time_calc = time_now-time_cart
                print(time_calc[1])
                cart_time = Time(0, time_calc[0], time_calc[1], time_calc[2]).sum()
                print(cart_time)
                try:
                    the_cart = Cart.objects.get(id = carts[len(carts)-1].id)
                    if cart_time < 3600:
                        restart = False
                    else:
                        restart = True
                        data = {}
                        data['cart_closed'] = True
                        serializer = CartSerializer(the_cart, data = data, partial = True)
                        if serializer.is_valid():
                            serializer.save()
                    print('true')
                except ObjectDoesNotExist:
                    the_cart = None
                    print('hakulaloto')
                    restart=True
            else:
                cart_time = dt.datetime(year=2023, month=3, day=1, hour=0,minute=0,second=0)
                restart=True
                print('ndarasika')

            try:
                cart = Cart.objects.filter(customer_id = customer_contact[0].id).order_by('date')[0:1].get()
                print('true1')
                my_cart = CartSerializer(cart)
                the_list = json.loads(my_cart['product_list'].value)
                response7 = ''
                total=0
                for i in the_list['data']:
                    response = '{} {}kgs costing ${}\n'.format(i['product'], i['amount'], i['cost'])
                    response7 += response
                    total+=i['cost']
                response2 = 'Total cost is ${}'.format(total)
            except ObjectDoesNotExist:
                cart = {}
                print('false1')
                response7 = 'No carts exist yet please create one'
                response2 = 'yet!'

        

            if messages:
                a1 = len(messages)-1
                a2 = len(messages)-2
                a3 = len(messages)-3
                a4 = len(messages)-4

            # This is the first message that the bot will recognise 

            order = {}

            if incoming_message == 'hello':
                data = {'phonenumber': phonenumber}
                serializer = CustomerSerializer(data=data)
                if serializer.is_valid():
                        serializer.save()
                order = {}

                # The condition checks if the contact was found  in the database or if it should add the contact as a new entry
                # If the contact was saved in the database then customer gets the menu of options availabel
                if customer_contact:
                    order['customer'] = customer_contact[0].id
                    order['phonenumber'] = phonenumber
                    order['message'] = incoming_message
                    serializer2 = OrderSerializer(data = order)
                    if serializer2.is_valid():
                        serializer2.save()
                        print('saved')
                    response1='Hi {0} I am Agrostock your number one agricultural produce shop. I buy and sell agricultural produce'.format(phonenumber)
                    response='''How can i help you:

1. Make purchase
2. Request catalogue
3. Customer service
4. Merchant
5. View Cart
                                                
Select an option by typing A then the 
number of the option selected.'''
                    msg.body(response1 + response)
                    return HttpResponse(str(resp))
                else:
                    data = {'phonenumber': phonenumber}
                    serializer3 = CustomerSerializer(data=data)
                    if serializer3.is_valid():
                        serializer3.save()
                    response = 'Hie welcome to our agrostock bot please send us a Hello and we will get started with you'
                    msg.body(response)
                    return HttpResponse(str(resp))
                

            elif incoming_message == 'cart':
                msg.body(response7+response2)
                return HttpResponse(str(resp))
            # The chain begins after a hello has been found in the messages database and the options begin to play around
            elif incoming_message == '0':
                print('seen')
                print(restart)
                if restart == False:
                    order['customer'] = customer_contact[0].id
                    order['phonenumber'] = phonenumber
                    order['message'] = incoming_message
                    serializer2 = OrderSerializer(data = order)
                    if serializer2.is_valid():
                        serializer2.save()
                    
                msg.body(message)
                return HttpResponse(str(resp))


            elif messages[a1].message == '0':
                products = Product.objects.filter(index = int(incoming_message))
                product = products[0]
                print('here here')
                if products:
                    order['customer'] = customer_contact[0].id
                    order['phonenumber'] = phonenumber
                    order['message'] = incoming_message
                    serializer2 = OrderSerializer(data = order)
                    if serializer2.is_valid():
                        serializer2.save()
                    response = 'How many kgs of {} do you want?'.format(product.product)
                    
                    msg.body(response)
                    return HttpResponse(str(resp))
                else:
                    return HttpResponse('Please restart from hello')


            elif messages[a2].message == '0':
                products = Product.objects.filter(index = int(messages[a1].message))
                product = products[0]
                if messages[a1].message == str(product.index):
                    cart2 = '1'
                    product1 = incoming_message
                    if incoming_message != None:
                        x = messages[a1].message
                        cost = product.price*int(incoming_message)
                        if restart == True:
                            data = {}
                            product_list = json.dumps({'data':[{'product_index': product.index, 'product': product.product, 
                            'price_per_unit': int(product.price), 'amount': int(incoming_message), 
                            'cost': int(cost)}]})
                            data['customer'] = customer_contact[0].id
                            data['product_list'] = product_list
                            data['cost'] = cost
                            data['product'] = product.id
                            data['cart_closed'] = False
                            serializer = CartSerializer(data = data)
                            if serializer.is_valid():
                                serializer.save()
                        else:
                            data = {}
                            the_list = json.loads(the_cart.product_list)
                            the_list['data'].append({'product_index': product.index, 'product': product.product, 
                            'price_per_unit': int(product.price), 'amount': int(incoming_message), 
                            'cost': int(cost)})
                            product_list = json.dumps(the_list)
                            for i in the_list['data']:
                                cost += i['cost']
                            data['customer'] = the_cart.customer.id
                            data['product_list'] = product_list
                            data['cost'] = cost
                            data['product'] = product.id
                            data['cart_closed'] = False
                            serializer = CartSerializer(the_cart, data = data, partial = True)
                            if serializer.is_valid():
                                serializer.save()
                                print('saved')
                        response = '''It will cost ${0}.
If you would like to order another product send 0.
If you are done or to view cart send cart'''.format(cost)
                        msg.body(response)
                        return HttpResponse(str(resp))            
                        

            elif messages[a1].message == 'hello':
                                
                #Place order to see product list
                if incoming_message == '1':
                    order['customer'] = customer_contact[0].id
                    order['phonenumber'] = phonenumber
                    order['message'] = incoming_message
                    serializer2 = OrderSerializer(data = order)
                    if serializer2.is_valid():
                        serializer2.save()
                    responses = []

                    print(message)
                    msg.body(message)
                    return HttpResponse(str(resp))

                elif incoming_message == '3':
                    response='''Please type the problem code eg "*c1*" at the beginning of your problem statement
1. Ask for help?
2. Report a problem?

Thank you. We will get back to you'''

                    msg.body(response)
                    return HttpResponse(str(resp))

                elif incoming_message == '6':
                    response='Redirect to the organisation website'
                    msg.body(response)
                    return HttpResponse(str(resp))

                elif incoming_message == '2':
                    GOOD_BOY_URL = (
                        "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?ixlib=rb-1.2.1"
                        "&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80"
                    )
                    response1 = '''NDICHAISA URL'''
                    msg.body(response1)
                    msg.media(GOOD_BOY_URL)
                    return HttpResponse(str(resp))


            elif messages[a2].message == 'hello':
                if messages[a1].message == '1':
                    products = Product.objects.filter(index = int(incoming_message))
                    product = products[0]

                    if products:
                        order['customer'] = customer_contact[0].id
                        order['phonenumber'] = phonenumber
                        order['message'] = incoming_message
                        serializer2 = OrderSerializer(data = order)
                        if serializer2.is_valid():
                            serializer2.save()
                        response = 'How many kgs of {} do you want?'.format(product.product)
                    
                    msg.body(response)
                    return HttpResponse(str(resp))
                else:
                    return HttpResponse('Please restart from hello')
                        

            elif messages[a3].message == 'hello':
                if messages[a2].message == '1':
                    products = Product.objects.filter(index = int(messages[a1].message))
                    product = products[0]

                    if messages[a1].message == str(product.index):
                        cart2 = '1'
                        product1 = incoming_message
                        if incoming_message != None:
                            x = messages[a1].message
                            cost = product.price*int(incoming_message)
                            if restart == True:
                                data = {}
                                product_list = json.dumps({'data':[{'product_index': product.index, 'product': product.product, 
                                'price_per_unit': int(product.price), 'amount': int(incoming_message), 
                                'cost': int(cost)}]})
                                data['customer'] = customer_contact[0].id
                                data['product_list'] = product_list
                                data['cost'] = cost
                                data['product'] = product.id
                                data['cart_closed'] = False
                                serializer = CartSerializer(data = data)
                                print('new')
                                print(serializer.is_valid())
                                print(serializer.errors)
                                if serializer.is_valid():
                                    serializer.save()
                                    print('new1')
                            else:
                                data = {}
                                the_list = json.loads(the_cart.product_list)
                                the_list['data'].append({'product_index': product.index, 'product': product.product, 
                                'price_per_unit': int(product.price), 'amount': int(incoming_message), 
                                'cost': int(cost)})
                                product_list = json.dumps(the_list)
                                for i in the_list['data']:
                                    cost += i['cost']
                                data['customer'] = the_cart.customer.id
                                data['product_list'] = product_list
                                data['cost'] = cost
                                data['product'] = product.id
                                data['cart_closed'] = False
                                serializer = CartSerializer(the_cart, data = data, partial = True)
                                print('old')
                                if serializer.is_valid():
                                    serializer.save()
                                    print('old1')
                            response = '''It will cost ${0}.
If you would like to order another product send 0.
If you are done or to view cart send cart'''.format(cost)
                            msg.body(response)
                            return HttpResponse(str(resp))


            