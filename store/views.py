from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime
from . utils import coockieCart,cartData,guestOrder
# Create your views here.

def store(request):
    data = cartData(request)
    
    items = data['items']
    cartItems = data['cartItems']
    order = data['order']
            
    products = Product.objects.all()
    context = {'products':products,'get_cart_items': cartItems} 
    return render(request,'store/Store.html',context)

def checkout(request):
    data = cartData(request)
    
    items = data['items']
    cartItems = data['cartItems']
    order = data['order']
    context = {'items':items,'order':order,'get_cart_items':cartItems}
    return render(request,'store/Checkout.html',context)

def cart(request):
    data = cartData(request)

    items = data['items']
    cartItems = data['cartItems']
    order = data['order']
      
    context = {'items':items,'order':order,'get_cart_items':cartItems}
    return render(request,'store/Cart.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print(productId +' ' + action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer = customer,complete = False)

    orderItem, created = OrderItem.objects.get_or_create(order= order, product = product)
    
    if action =='add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action=='remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()    

    if orderItem.quantity <= 0:
        orderItem.delete()
    

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp() 
    data = json.loads(request.body)
    print('json',data)
    if request.user.is_authenticated:
        customer = request.user.customer  
        order,created = Order.objects.get_or_create(customer=customer,complete = False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        
    else:
        customer , order = guestOrder(request, data)
        print("User is not logged in")
        print("COOKIES:",request.COOKIES)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
                ShippingAddress.objects.create(
                    customer = customer,
                    order= order,
                    address= data['shipping']['address'],
                    city= data['shipping']['city'],
                    state= data['shipping']['state'],
                    zipcode= data['shipping']['zipcode']
                )

    return JsonResponse('payment complete',safe = False)