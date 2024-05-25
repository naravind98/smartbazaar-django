from django.contrib import admin
from .models import Category


# The 'Category' model has been registered here in admin.py so that we can see the Category object details
# in django admin. To have more control on how these details should be displayed (for ex: which all details
# do we need to display, which details should displayed as links, which ones should be read-only, in which
# order do we need to display details) we are creating this class 'CategoryAdmin' by extending
# 'admin.ModelAdmin' class which has inbuilt attributes/variables defined.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}  # category_name is the 1st field of Category model
    list_display = ('category_name', 'slug')


# Register your models here.
admin.site.register(Category, CategoryAdmin)
