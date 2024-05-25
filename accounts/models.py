from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.

# We first created the Account model(i.e. around line-50) for normal users. Okay, so next we want to
# create a model for superadmin. Right? We created a superadmin(i.e. superuser) and we were logging in with
# the username, so we want to override that. We want to create a custom user model(which we did above i.e.
# 'Account') and now we need to create a model for our superadmin.
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError("User must have an email address")

        if not username:
            raise ValueError("User must have a username")

        user = self.model(
            email=self.normalize_email(email),
            # So what this normalize_email(email) does is if you enter any capital letter email address, then it will just make it as a small letter. Everything will be normalized.
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(
            password)  # set_password(password) is used for setting the password. this is actually the inbuilt function.
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # We need to give the permission. Because this is not a simple user. This is a super user. That's why we have to set all the permission to true.
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


# Creating a custom user model
class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)

    """ Because we are implementing a custom user model, we have to mention some required fields here  
    The below 5-6 fields are mandatory when we are creating a custom user model """
    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    """ So, so once this is done, we need to set the login field, right? So currently by default 'username' 
    is our login field, right? But in our application, we want to login with our "email address", not 
    'username'. So for that, what we need to set 'USERNAME_FIELD' is equal to 'email' """

    USERNAME_FIELD = 'email'  # because we defined -> email = models.EmailField(max_length=100, unique=True)......Inbuilt variable
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']  # inbuilt variable

    objects = MyAccountManager()              # tell the 'Account' class that we are using the 'MyAccountManager'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):  # Returns True if the user has the named permission. If obj is provided, the permission needs to be checked against a specific object instance. In-built function.
        return self.is_admin

    def has_module_perms(self, app_label):  # Returns True if the user has permission to access models in the given app. In-built function.
        return True

