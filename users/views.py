import os

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import SignupForm
from .models import User
from .tokens import account_activation_token


def activate_account(request, uidb64, token, *args, **kwargs):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        login(request, user)
        messages.success(request, 'Your account has been confirmed.')
        return redirect('home')
    else:
        messages.warning(request, 'The confirmation link is invalid.')
        return redirect('home')


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            msg = render_to_string("users/confirmation_email.html", {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            send_mail('Activate your account - FaceIt', msg, os.environ['EMAIL_USER'], [user.email],
                      html_message=msg)

            messages.success(request, f'Your account has been created! Please confirm email address.')
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            form.clean()
            login(request, form.get_user())
            return redirect(request.GET.get('next') or 'home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
