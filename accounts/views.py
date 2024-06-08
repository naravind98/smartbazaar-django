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
            auth.login(request, user)
            messages.success(request, "You are now logged in")
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

