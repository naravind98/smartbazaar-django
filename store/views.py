from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse


# Create your views here.
def store(request, category_slug=None):
    """ When you click on the store button or when you click on a particular category, the respective
     products should be shown. If you click on the store button, all the products should be displayed. If
     you click on a particular category all the products related to that category should be displayed. For
     this purpose, the function store() is implemented"""
    if category_slug:
        requested_category = get_object_or_404(Category,
                                               slug=category_slug)  # In the 1st arg we mention that the object we need is in Category model and the 2nd arg is 'slug' which is the attribute of Category model class using which we locate the specific/requested category.
        products = Product.objects.all().filter(category=requested_category, is_available=True).order_by('id')       # if we dont use 'order_by('id')' the code still works but we get a warning message -> UnorderedObjectListWarning: Pagination may yield inconsistent
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')

    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()
    context = {
        "products": paged_products,
        "product_count": product_count,
    }
    return render(request, "store/store.html", context)


def product_detail(request, category_slug=None, product_slug=None):
    """ When you click on the "View Details" button of a particular product or when you click img/
    name of that particular product, you should be able to see the details of that product. This
    function is triggered for that purpose. It fetches that product object from the db.  """
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)    # in the 1st arg "category__slug" -> 'category' is one of the fields of 'Product' model and 'slug' is one of the fields of Category so the value of "category_slug" goes to the category object's slug field
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()      # This boolean flag checks if this product is already present in the cart or not.
        context = {
            'single_product': single_product,
            'in_cart': in_cart,
        }
    except Exception as e:
        raise e

    return render(request, "store/product_detail.html", context)


def search(request):
    """ When you search for products with a keyword in the search-form in navbar.html, those products should
     be displayed whose 'product_name' or 'description' contain that keyword. The search() function use that
     keyword to fetch products from db."""
    if 'keyword' in request.GET:                 # check the form-search functionality in navbar.html. Whatever you submit in the search it will be passed in the url. For ex. if you submit 'shirt' in the Search then the url will be "http://127.0.0.1:8000/store/search/?keyword=shirt"
        keyword = request.GET['keyword']
        if keyword:
            # products = Product.objects.order_by('-created_date').filter(description__icontains=keyword,
            #                                                             product_name__icontains=keyword)     # Inside the filter we mentioned 2 fields (i.e. description and product_name) to lookup the 'keyword' but the 2 fields are seperatd by comma (,) so this filter query will treated as an AND operation.
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) |
                                                                        Q(product_name__icontains=keyword))    # In order to use the OR operation we have make use of Q
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }

    return render(request, "store/store.html", context)


