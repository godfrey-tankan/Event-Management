from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserRegistrationForm, \
                   UserEditForm, ProfileEditForm
from .models import Profile
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
                    return HttpResponse('Authenticated successfully')
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


# def register(request):
#     """
#     View function for user registration.

#     Allows users to register for a new account.

#     Parameters:
#         request (HttpRequest): The HTTP request object.

#     Returns:
#         HttpResponse: HTTP response containing registration form.
#     """
#     if request.method == 'POST':
#         user_form = UserRegistrationForm(request.POST)
#         if user_form.is_valid():
#             # Create a new user object but avoid saving it yet
#             new_user = user_form.save(commit=False)
#             # Set the chosen password
#             new_user.set_password(user_form.cleaned_data['password'])
#             # Save the User object
#             new_user.save()

#             try:
#                 # Data for QR code generation
#                 user_data = {
#                     'username': new_user.username,
#                     'email': new_user.email,
#                     # Add any other user data you want to include
#                 }
                
#                 # Convert user data to a string
#                 data_str = ", ".join([f"{key}: {value}" for key, value in user_data.items()])
                
#                 # Generate QR code
#                 qr = qrcode.QRCode(
#                     version=1,
#                     error_correction=qrcode.constants.ERROR_CORRECT_L,
#                     box_size=10,
#                     border=4,
#                 )
#                 qr.add_data(data_str)
#                 qr.make(fit=True)
                
#                 # Generate QR code image
#                 qr_image = qr.make_image(fill_color="black", back_color="white")
                
#                 # Define directory for saving QR codes
#                 qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
#                 os.makedirs(qr_code_dir, exist_ok=True)
                
#                 # Define file path for saving QR code image
#                 qr_code_path = os.path.join(qr_code_dir, f'user_{new_user.id}_qr_code.png')
                
#                 # Save QR code image
#                 qr_image.save(qr_code_path)
                
#                 # Create the user profile
#                 Profile.objects.create(user=new_user, qr_code=os.path.relpath(qr_code_path, settings.MEDIA_ROOT))
#                 print(f"QR code created and saved for user: {new_user.username}")
#             except Exception as e:
#                 print(f"Error creating QR code for user {new_user.username}:")
#                 print(traceback.format_exc())

#             return render(request, 'account/register_done.html', {'new_user': new_user})
#     else:
#         user_form = UserRegistrationForm()
#     return render(request, 'account/register.html', {'user_form': user_form})




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
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
                                    instance=request.user.profile,
                                    data=request.POST,
                                    files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated '\
                                      'successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(
                                    instance=request.user.profile)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})
