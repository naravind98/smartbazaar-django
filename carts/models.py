from django.db import models
from store.models import Product, Variation
from accounts.models import Account


# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):                        # When a product is added to a cart that product becomes cartitem i.e. an an object of class CartItem
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)            # we are assigning user as an attribute bcoz if there are some cart-items in the cart and then a user logs-in then the cartitems should still be present in the cart.
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_available = models.BooleanField(default=True)

    """ This function will calculate the total price of a cart-item. For ex. if we add 3 'Mavi-jeans' to cart 
     then the total price will 3*499. The price of 'Mavi-jeans' is 499 """
    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product

    # def __str__(self):
    #     return f"Username:{self.user.username}--{self.variations}--Cart:{self.cart}"
