from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Imports to send verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                               email=email, password=password)
            user.phone_number = phone_number             # The Account class does not have 'phone_number' attribute.
            user.save()

            # USER ACTIVATION - sending mail to verify the user. The mail will contain activation link.
            current_site = get_current_site(request)                        # Now we are using Localhost but later we might deploy in a production server and then the domain of the current site will not be localhost
            mail_subject = "Please Activate your Account."
            message = render_to_string("accounts/account_verification_email.html", {
                'user': user,                                               # This is the user object which we can use to fetch the name in the email html-template
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),         # 'uid' is user-id i.e. the primary-key of the user object. urlsafe_base64_encode(force_bytes(user.pk)) function will encode the primary-key.
                'token': default_token_generator.make_token(user),          # default_token_generator is the library which has make_token() function which will generate token for each user.
            })                                                              # 'render_to_string' is used to send the body of the email. This function is similar to render() function where we pass html-template and context-dictionary inside the render function. In this function we are passing the html-template for the email. Also we are passing context-dictionary which we can use inside the email htmml-template.
            to_email = email                             # the email-id(provided during registration) to which we need to send the mail with activation link
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, "Thank you for registering with us. We have sent you a verification email to "
            #                           "your email address. Please verify it.")
            # return redirect('register')

            # here we are redirecting to url 'accounts/login/?command=verification&email='+email' where 'command'
            # and 'email' are url-inputs/parameters with values 'verification' and 'email-from code' respectively.
            # These 2 key-value pairs will be used in login.html page to print a specific msg i.e. "Thank you for
            # registering with us. We have sent you a verification email to your email address. Please verify it.""
            return redirect('/accounts/login/?command=verification&email='+email)            # if you pass 'accounts/login/?command=verification&email=' inside redirect without adding '/' before 'accounts' then you will get error.

    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']             # we get the input which was named as 'email' in login.html
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            """ The below try-except block has nothing to do with the login functionality. After the try-except
            block the user is logged-in by the line "auth.login(request, user)". In this try-except block we
            are grouping the cart_items based on variation (i.e. if there are 2 cart_item having variation as
            (Blue, Medium) then the cart_item should be shown once with quantity as 2). We have to consider 2 
            scenarios. 
            Scenario-1: When the user login for the 1st time and there is no product in the cart. And then the 
            user add 3 products in the cart. This cart will contain 3 cart_items with a user. They will be grouped 
            (based on variation) because of the grouping-code in add_cart() view function.
            Scenario-2: After adding 3 items the user logs out. Then the cart will show 0 products. Now you add
            4 products in the cart. These 4 cart_items will not have the user(i.e. their user attribute will be None) 
            because the user is not logged-in yet. These 4 cart_items will also be grouped because of the add_cart() 
            view function. Now after adding these 4 products in cart the user will want to checkout. The checkout()
            view function will force the user to login. After the user logs-in, we need to add the 4 cart_items
            which didn't have the user attribute to the 3 cart_items which are grouped and have the user attribute.
            We should add in such a way that the cart_items should be placed in respective variation-group and also
            set the user attribute for these 4 cart_items."""
            try:
                """ Here we will check if there are any cart_items already present in the cart. If yes, then to all
                 those cart_items we are assigning the user who logged-in"""
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                # print("is_cart_item_exists", is_cart_item_exists)
                """ The below if checks if before logging-in were there any cart_items present in the cart """
                if is_cart_item_exists:
                    # print("inside if is_cart_item_exists")
                    """ The below if condition checks whether there are any cart_items having the user
                     attribute equal to this user. If true, then we have to do the grouping of cart_items 
                     accordingly. """
                    if CartItem.objects.filter(user=user).exists():
                        # Scenario-2
                        cart_items = CartItem.objects.filter(cart=cart)
                        # Getting the product_variations for Scenario-2
                        product_variation = []
                        cart_item_id_list1 = []
                        for item in cart_items:
                            variation = item.variations.all()
                            product_variation.append(list(variation))     # After for-loop, each item of the product_variation list will be a list of variations of a particular cart_item
                            cart_item_id_list1.append(item.id)
                        # Scenario-1
                        cart_items = CartItem.objects.filter(user=user)
                        product_variation_user = []                 # Each item in this list will be a list of variations of a particular cart_item
                        cart_item_id_list2 = []                           # This is a list of id's of particular cart_item
                        for item in cart_items:
                            variation_user = item.variations.all()
                            product_variation_user.append(list(variation_user))
                            cart_item_id_list2.append(item.id)

                        # Now we add cart_items of Scenario-2(without user) to the groups of cart_items of Scenario-1(with user)
                        for pr_var in product_variation:
                            if pr_var in product_variation_user:
                                # print("Inside if where pr_var have user")
                                index = product_variation_user.index(pr_var)
                                cart_item_id = cart_item_id_list2[index]
                                cart_item = CartItem.objects.get(id=cart_item_id)
                                cart_item.quantity += 1
                                # cart_item.user = user
                                cart_item.save()
                            else:
                                index = product_variation.index(pr_var)
                                cart_item_id2 = cart_item_id_list1[index]
                                cart_item = CartItem.objects.get(id=cart_item_id2)
                                cart_item.user = user
                                cart_item.save()

                    else:
                        cart_items = CartItem.objects.filter(cart=cart)
                        for item in cart_items:
                            item.user = user
                            item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            """ The purpose of the below code is to get the next url to which we need to go incase there is a next url else go to the dashboard """
            # print("CURRENT URL", request.build_absolute_uri())             # This gives the current url -> Output: http://127.0.0.1:8000/accounts/login/
            # print("request.get_full_path()", request.get_full_path())      # This also gives the full path of current url -> Output: /accounts/login/
            # print("request.path", request.path)                            # Same as above -> Output: /accounts/login/
            url = request.META.get('HTTP_REFERER')            # This gives you the next url to which we need to go. See the below output. The next url to which we need to go is "/cart/checkout/". That is why we are using "HTTP_REFERER"
            print("*****url******", url)                      # Output: *****url****** http://127.0.0.1:8000/accounts/login/?next=/cart/checkout/
            # print("type:", type(url))                         # Output: type: <class 'str'>
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')

    return render(request, "accounts/login.html")


@login_required(login_url='login')               # This makes sure that the below function is triggered if and only if users are logged in. If they are not logged in and try to forcefully go to "http://127.0.0.1:8000/accounts/logout/" without logging in then the login page will be shown.
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out")
    return redirect('login')
    # return render(request, "accounts/logout.html")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()              # we decode the input parameter 'uidb64' to get the primary key which was encoded in the register() view function
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect('login')
    else:
        messages.error(request, "Invalid Activation Link")
        return redirect('register')
    # return HttpResponse(f"The activate view is working.......uidb64:{uidb64}........token:{token}")


@login_required(login_url='login')               # This makes sure that the below function is triggered if and only if users are logged in. If they are not logged in and try to forcefully go to "http://127.0.0.1:8000/accounts/dashboard/" without logging in then the login page will be shown.
def dashboard(request):
    return render(request, "accounts/dashboard.html")
    # return HttpResponse("The dashboard view is working")


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']            # The POST['email'] will get you the email-input from the forgotPassword.html
        if Account.objects.filter(email__exact=email).exists():       # email__exact is case-sensitive, email__iexact is case-insensitive
            user = Account.objects.get(email__iexact=email)

            current_site = get_current_site(request)  # Now we are using Localhost but later we might deploy in a production server and then the domain of the current site will not be localhost
            mail_subject = "Reset your Password."
            message = render_to_string("accounts/reset_password_email.html", {
                'user': user,  # This is the user object which we can use to fetch the name in the email html-template
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # 'uid' is user-id i.e. the primary-key of the user object. urlsafe_base64_encode(force_bytes(user.pk)) function will encode the primary-key.
                'token': default_token_generator.make_token(user),
                # default_token_generator is the library which has make_token() function which will generate token for each user.
            })  # 'render_to_string' is used to send the body of the email. This function is similar to render() function where we pass html-template and context-dictionary inside the render function. In this function we are passing the html-template for the email. Also we are passing context-dictionary which we can use inside the email htmml-template.
            to_email = email  # the email-id(provided during registration) to which we need to send the mail with activation link
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, "Password reset email has been sent to your email address")
            return redirect('login')

        else:
            messages.error(request, "The account with this email-id does not exist")
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')


def reset_password_validate(request, uidb64, token):
    """ This function is triggered when the user clicks on the link in reset_password_email.html. The purpose of
      this function is not to reset password. This function checks if the user who is trying to reset the password
      is a valid user or not. If the user is valid then the uid of the user is set as the session of this current
      request.     """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()              # we decode the input parameter 'uidb64' to get the primary key which was encoded in the register() view function
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid                  # Here we are saving the uid inside the session of current request so that we can access this session later when we are resetting the password
        messages.success(request, "Please reset your password")
        return redirect('resetPassword')
    else:
        messages.error(request, "This link has been expired")
        return redirect('login')


def reset_password(request):                     # In this request the session-id will be the uid which we had set in the reset_password_validate() view function
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect('login')

        else:
            messages.error(request, "The password does not match")
            return redirect('resetPassword')
    else:
        return render(request, "accounts/resetPassword.html")

