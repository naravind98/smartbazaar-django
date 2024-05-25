from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin


# The 'Account' model has been registered here in admin.py so that we can see the Account object details
# in django admin. To have more control on how these details should be displayed (for ex: which all details
# do we need to display, which details should displayed as links, which ones should be read-only, in which
# order do we need to display details) we are creating this class 'AccountAdmin' by extending 'UserAdmin'
# class which has inbuilt attributes/variables defined.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)                      # for tuple with single item .....make sure to put the comma after else it wont be considered as tuple

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


# Register your models here.
admin.site.register(Account, AccountAdmin)

