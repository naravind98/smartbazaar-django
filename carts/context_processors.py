from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))       # There should only be 1 cart which matches the cart_id. So we could have used get() instead of filter() but if we used get() there ia a possibility to get 'ObjectNotExist' exception. So to avoid that we are using filter()
            cart_items = CartItem.objects.filter(cart=cart[:1])         # In the previous line, we are getting a 'QuerySet' which is an iterable. But in the above line of code, the 'QuerySet' will contain only a single 'Cart' object which matches the cart_id. Therefore in this line, we used slicing to get that single object.
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.ObjectNotExist:
            cart_count = 0

    count_dict ={
        'cart_count': cart_count,
    }
    return count_dict
    # return dict(cart_count=cart_count)

