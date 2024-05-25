from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category


# Create your views here.
def store(request, category_slug=None):
    if category_slug:
        requested_category = get_object_or_404(Category,
                                               slug=category_slug)  # In the 1st arg we mention that the object we need is in Category model and the 2nd arg is 'slug' which is the attribute of Category model class using which we locate the specific/requested category.
        products = Product.objects.all().filter(category=requested_category, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)
    product_count = products.count()
    context = {
        "products": products,
        "product_count": product_count,
    }
    return render(request, "store/store.html", context)


def product_detail(request, category_slug=None, product_slug=None):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)    # in the 1st arg "category__slug" -> 'category' is one of the fields of 'Product' model and 'slug' is one of the fields of Category so the value of "category_slug" goes to the category object's slug field
        context = {
            'single_product': single_product,
        }
    except Exception as e:
        raise e

    return render(request, "store/product_detail.html", context)

