from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist


def _cart_id(request):  # The single-underscore before the function-name is to indicate that this function is private.
    """ In this function the session-id(session_key) is fetched and returned. We use this session-id as the
    cart-id """
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_cart(request, product_id):
    """ In this we are adding a product to a cart and thereby making the product a cart_item.
    When a product is added to cart, that product becomes a cart_item """
    product = Product.objects.get(id=product_id)  # here id is the primary key of 'Product' model. This 'id' field is created by-default by django when a model class is created and migrated.
    product_variation = []         # This list will contain 'Variation' objects. Each 'Variation' objects will be the variation that we selected for the above product and it is with these variations we want to add this product to the cart. For ex. if we want to add 'ATX-Jeans' in the cart of color:Blue and size:Large then this list will have 2 variation objects i.e [ATX-Jeans--Color--Blue, ATX-Jeans--Size--Large]. In short, 'product_variation' will be a list of variations associated to a particular product.
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                  variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # getting the cart using the cart_id present in the session
    except Cart.ObjectDoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    finally:
        cart.save()

    cart_item = None
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        # print("is_cart_item_exists:", is_cart_item_exists)
        cart_items = CartItem.objects.filter(product=product, cart=cart)       # collection of cart-item. basically a querryset
        ex_var_list = []
        list_id = []
        for item in cart_items:
            existing_variation = item.variations.all()      # 'existing_variation' will contain a collection of all the variations associated to a particular cart-item i.e. 'item' in this line of code. But 'existing_variation' is a queryset not a list. Therefor in the next line we convert it to list so that it is easy to iterate.
            ex_var_list.append(list(existing_variation))    # after the for-loop, 'ex_var_list' will be a list of lists where each list will contain variations associated to each cart-item in the cart. For eg. [[ATX-Jeans--Color--Blue, ATX-Jeans--Size--Large],[Wrangler-Shirt--Color--Red, Wrangler-Shirt--Size--Small],[Jordan-Shoes--Color--Black, Jordan-Shoes--Size--Medium]]
            list_id.append(item.id)                         # after the for-loop, 'list_id' will be a list of id's(primary-key of cart-item object i.e. id) of each cart-items present in the cart. For eg. [id_of_cart-item_ATX-Jeans, id_of_cart-item_Wrangler-Shirt, id_of_cart-item_Jordan-Shoes]

            # Note: 'ex_var_list' is a list of variations of each cart-item. 'list_id' is a list of primary-key id of each cart-item. 'ex_var_list' and 'list_id' has 1:1 relation. Therefore if 'product_variation' exists in 'ex_var_list' then using the corresponding id of cart-item, we can increment the quantity of that particular cart-item.

        # print("ex_var_list:", ex_var_list)
        # print("product_variation", product_variation)

        if product_variation in ex_var_list:
            # print("product_variation exists in ex_var_list")
            """ increase the cart-item's quantity """
            index = ex_var_list.index(product_variation)
            cart_item_id = list_id[index]
            cart_item = CartItem.objects.get(product=product, id=cart_item_id)
            cart_item.quantity += 1

        else:
            # print("product_variation does not exists in ex_var_list")
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)

    else:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1,
        )

    if len(product_variation) > 0:
        # cart_item.variations.clear()
        # for item in product_variation:
        #     cart_item.variations.add(item)
        cart_item.variations.add(*product_variation)         # Instead of looping, we can use *product_variation. This will add all the variation objects in one go.
        cart_item.save()                                     # instead of saving the cart_item at multiple places, I am giving the save() at one place and that too at the end of the function
        # print(cart_item.product, cart_item.variations)

    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    """ When the minus button is clicked for a particular cart_item in the cart, the quantity of that
      cart_itme need to be decremented by 1 if the quantity is > 1 else that cart_item should be deleted  """
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


# def cart(request):
def cart(request, total_price=0, total_quantity=0, cart_items=None):
    """ In this function, we fetch the cart_items of the current cart, calculate the total_price,
     total_quantity and return cart_items, total_price and total_quantity in the context-dictionary to the
     cart.html """
    try:
        # total_price, total_quantity, cart_items = 0, 0, None
        cart = Cart.objects.get(cart_id=_cart_id(request))  # cart_id is one of the field of Cart model class
        cart_items = CartItem.objects.filter(cart=cart,
                                             is_available=True)  # 'cart' is one of the field of Cart model class
        for cart_item in cart_items:
            total_price += (cart_item.product.price * cart_item.quantity)
            total_quantity += cart_item.quantity
        tax = (2 * total_price) / 100
        grand_total = total_price + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, "store/cart.html", context)
