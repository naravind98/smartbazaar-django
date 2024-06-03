from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),           # if we dont add 'category' in the pattern then the 'search' in the url "http://127.0.0.1:8000/store/search/" is treated as a category-slug. Therefore we explicitly added 'category' in the 1st arg i.e. pattern-matching
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path("search/", views.search, name='search'),
]

