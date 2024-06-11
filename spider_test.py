from carts.models import CartItem


cart_items = list(CartItem.objects.filter(cart_cart_id='5q5o7mckgv3vk8rcbuoqzceopqb5ez4g'))

print(len(cart_items))

