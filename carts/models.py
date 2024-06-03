from django.db import models
from store.models import Product, Variation


# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):                        # When a product is added to a cart that product becomes cartitem i.e. an an object of class CartItem
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_available = models.BooleanField(default=True)

    """ This function will calculate the total price of a cart-item. For ex. if we add 3 'Mavi-jeans' to cart 
     then the total price will 3*499. The price of 'Mavi-jeans' is 499 """
    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product
