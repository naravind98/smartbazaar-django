from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order
import datetime
import json

# Create your views here.


def place_order(request, total=0, quantity=0,):
    """ In the checkout.html, after providing the billing address we have to click on the "Place Order"
    button which will trigger this function. Here, first we check if there are any cart_items present then
    calculate the grand_total,tax. After that if the form is valid we create the Order object, set the
    available details/attributes and save it. Finally render the payments.html file along with context """
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)             # id in data.id is the primary key of Order model
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)    # Just above we saved an Order object called data. We are fetching the same object here. When we saved this object above, we didn't explicitly set the 'is_ordered' attribute. So by default it was set to 'False'. There we used "is_ordered=False" in filter
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def payments(request):
    body = json.loads(request.body)
    print(body)                                           # {'orderID': '202406149', 'transID': '6LU35551WN388143P', 'payment_method': 'PayPal', 'status': 'COMPLETED'}
    return render(request, 'orders/payments.html')
    # return HttpResponse("The payments view is working")


def order_complete(request):
    return HttpResponse("The order_complete view is working")
