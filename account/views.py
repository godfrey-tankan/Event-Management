from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserRegistrationForm, \
                   UserEditForm, ProfileEditForm
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ObjectDoesNotExist
import os
import qrcode
from django.conf import settings
import traceback


def user_login(request):
    """
    View function for user login.

    Allows users to log in to their accounts.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: HTTP response containing login form.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    """
    View function for the user dashboard.

    Provides access to the user's dashboard after successful login.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: HTTP response containing the user dashboard.
    """
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard'})

@login_required
def request_user_profile(request):
    """
    View function for requesting user profile.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: HTTP response containing the user profile.
    """
    user = request.user.id
    try:
        profile = Profile.objects.get(user=user)

        qr_code_url = profile.barcode.url

        response_data = {
            'profile': profile,
            'qr_code_url': qr_code_url,
        }

        return render(request, 'account/profile.html', response_data)
    except ObjectDoesNotExist:
        messages.error(request, 'Profile barcode does not exist')
        return redirect('dashboard')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Create the user profile
            Profile.objects.create(user=new_user)
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})


                  
@login_required
def edit(request):
    """
    View function for editing user profile.

    Allows users to edit their profile information.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: HTTP response containing profile editing form.
    """
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
    else:
        user_form = UserEditForm(instance=user)
    return render(request, 'account/register.html', {'user_form': user_form,"action":"edit"})