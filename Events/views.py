from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .forms import EventForm
from account.models import Profile
from django.http import HttpResponse
from .models import BarcodeScan
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Event, EventRegistration
from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone
import re
import qrcode
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt


# import cv2

@staff_member_required
@login_required
def create_event(request):
    """
    View function for creating an event.

    Only staff members (admins) can access this view.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: HTTP response containing the event creation form.
    """
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect('event_list')  # Redirect to event list after event creation
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})
@login_required
def event_list(request):
    """
    View function for displaying a list of events.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: HTTP response containing the list of events.
    """
    events = Event.objects.all()
    registered_events_id_list = []
    registered_events_list = EventRegistration.objects.filter(user=request.user.id)
    if registered_events_list:
        for registered_event in registered_events_list:
            registered_events_id_list.append(registered_event.event.id)
    registered_events = registered_events_list if registered_events_list else None
    return render(request, 'event_list.html', {'events': events, 'registered_events': registered_events, 'registered_events_id_list': registered_events_id_list})

@login_required
def register_for_event(request, event_id):
    """
    View function for registering for an event.

    Only logged-in users can access this view.

    Parameters:
        request (HttpRequest): The HTTP request object.
        event_id (int): The ID of the event to register for.

    Returns:
        HttpResponse: HTTP response redirecting to the event list page after registration.
    """
    # Get the event object from the database
    event = get_object_or_404(Event, id=event_id)
    
    # Check if the user is already registered for the event
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
    else:
        # Add the logged-in user to the attendees of the event
        EventRegistration.objects.create(event=event, user=request.user)
        messages.success(request, 'Successfully registered for the event.')
    
    return redirect('event_list')  # Redirect to event list after registration

@login_required
def unregister_event(request, event_id):
    """
    View function for unregistering from an event.

    Only logged-in users can access this view.

    Parameters:
        request (HttpRequest): The HTTP request object.
        event_id (int): The ID of the event to unregister from.

    Returns:
        HttpResponse: HTTP response redirecting to the event list page after unregistration.
    """
    # Get the event object from the database
    event = get_object_or_404(Event, id=event_id)
    
    # Check if the user is registered for the event
    registration = EventRegistration.objects.filter(event=event, user=request.user).first()
    if registration:
        registration.delete()
        messages.success(request, 'Successfully unregistered from the event.')
    else:
        messages.warning(request, 'You are not registered for this event.')
    
    return redirect('event_list')

@staff_member_required
@login_required
def delete_event(request, event_id):
    """
    View function for deleting an event.

    Only staff members (admins) can access this view.

    Parameters:
        request (HttpRequest): The HTTP request object.
        event_id (int): The ID of the event to delete.

    Returns:
        HttpResponse: HTTP response redirecting to the event list page after deletion.
    """
    event = get_object_or_404(Event, id=event_id)
    if event:
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('event_list')
    else:
        messages.error(request, 'Error deleting event.')
        return redirect('event_list')


@staff_member_required
@login_required
def edit_event(request, event_id):
    """
    View function for editing an event.

    Only staff members (admins) can access this view.

    Parameters:
        request (HttpRequest): The HTTP request object.
        event_id (int): The ID of the event to edit.

    Returns:
        HttpResponse: HTTP response containing the event edit form.
    """
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'create_event.html', {'form': form, 'event': event,"event_mode":"edit"})


@staff_member_required
@login_required
def view_event_attendees(request, event_id):
    """
    View function for viewing all users registered for an event.

    Only staff members (admins) can access this view.

    Parameters:
        request (HttpRequest): The HTTP request object.
        event_id (int): The ID of the event.

    Returns:
        HttpResponse: HTTP response containing the list of users registered for the event.
    """
    event = Event.objects.filter(id=event_id).all()
    attendees = event
    return render(request, 'event_attendees.html', {'event': event, 'attendees': event})



@staff_member_required
@login_required
def view_registered_users(request, event_id):
    """
    View function for displaying users registered for a specific event.

    Parameters:
        request (HttpRequest): The HTTP request object.
        event_id (int): The ID of the event for which registered users are to be displayed.

    Returns:
        HttpResponse: HTTP response containing the list of registered users for the event.
    """
    event = Event.objects.get(id=event_id)
    registered_users = EventRegistration.objects.filter(event=event)
    return render(request, 'registered_users.html', {'event': event, 'registered_users': registered_users})

def scan_barcode(request):
    last_scan_time = request.session.get('last_scan_time')
    if last_scan_time and (timezone.now() - datetime.fromisoformat(last_scan_time)) < timedelta(seconds=4):
        return JsonResponse({'message':None, 'time_taken': None, 'error': None})
    request.session['last_scan_time'] = timezone.now().isoformat()
    if request.method == 'POST':
        barcode_value_ob =  request.POST.get("barcode_value")
        try:
            barcode_value = ''.join(filter(str.isdigit, barcode_value_ob))
        except Exception as e:
            pass
        barcode_data = Profile.objects.filter(barcode_value=barcode_value).first()
        if barcode_data:
            barcode_scan = BarcodeScan.objects.filter(user=barcode_data.user).first()
            if barcode_scan is None:
                # First scan
                scan = BarcodeScan(user=barcode_data.user, scan_time=timezone.now())
                scan.save()
                return JsonResponse({'message': 'Please enjoy your race!', 'time_taken': None, 'error': None})
            else:
                # Subsequent scan
                if barcode_scan.time_taken:
                    message = f'This user {barcode_data.user.username} already participated Time taken: {barcode_scan.time_taken} seconds.'
                    time_taken = f'Time taken: {barcode_scan.time_taken} seconds.'
                    return JsonResponse({'message': message, 'time_taken': time_taken, 'error': None})

                scan_time = timezone.now()
                time_taken = (scan_time - barcode_scan.scan_time).total_seconds()
                barcode_scan.scan_time = scan_time
                barcode_scan.time_taken = time_taken
                barcode_scan.save()

                return JsonResponse({'message': None, 'time_taken': f'Time taken: {time_taken} seconds.', 'error': None})
        else:
            return JsonResponse({'message': None, 'time_taken': None, 'error': 'Scan Only Registered Users!'})
    else:
        return render(request, 'scan.html', {'current_url': request.path})
    
@csrf_exempt
def scan_barcode_mobile(request):
    last_scan_time = request.session.get('last_scan_time')
    if last_scan_time and (timezone.now() - datetime.fromisoformat(last_scan_time)) < timedelta(seconds=5):
        return JsonResponse({'message': None, 'time_taken': None, 'error': None})
    request.session['last_scan_time'] = timezone.now().isoformat()
    if request.method == 'POST':
        barcode_value_ob =  request.POST.get("barcode_value")
        try:
            barcode_value = ''.join(filter(str.isdigit, barcode_value_ob))
        except Exception as e:
            pass
        barcode_data = Profile.objects.filter(barcode_value=barcode_value).first()
        if barcode_data:
            registered_events = EventRegistration.objects.filter(user=barcode_data.user)
            if registered_events:
                barcode_scan = BarcodeScan.objects.filter(user=barcode_data.user).first()
                if barcode_scan is None:
                    # start scan
                    scan = BarcodeScan(user=barcode_data.user, scan_time=timezone.now())
                    scan.save()
                    return JsonResponse({'message': 'Race start, Please enjoy your race!', 'time_taken': None, 'error': None})
                else:
                    # finish scan
                    if barcode_scan.time_taken:
                        message = f'This user {barcode_data.user.username} already participated, Time taken: {barcode_scan.time_taken} seconds. '
                        time_taken = f'Time taken: {barcode_scan.time_taken} seconds.'
                        return JsonResponse({'message': message, 'time_taken': None, 'error': None})

                    scan_time = timezone.now()
                    time_taken = (scan_time - barcode_scan.scan_time).total_seconds()
                    barcode_scan.scan_time = scan_time
                    barcode_scan.time_taken = time_taken
                    barcode_scan.save()
                    return JsonResponse({'message': None, 'time_taken': f'Race Finished,Time taken: {time_taken} seconds.', 'error': None})
            else:
                return JsonResponse({'message': None, 'time_taken': None, 'error': 'User not registered for any event.'})
        else:
            return JsonResponse({'message': None, 'time_taken': None, 'error': 'No user Found.'})
    else:
        return render(request, 'mobile_scan.html')

def scan_QR_code_mobile(request):
    last_scan_time = request.session.get('last_scan_time')
    if last_scan_time and (timezone.now() - datetime.fromisoformat(last_scan_time)) < timedelta(seconds=3):
        return JsonResponse({'message': None, 'time_taken': None, 'error': None})
    request.session['last_scan_time'] = timezone.now().isoformat()
    
    if request.method == 'POST':
        barcode_value = request.POST.get('barcode_value', '')
        qr_code = qrcode.QRCode()
        qr_code.add_data(barcode_value)
        
        try:
            qr_code_data = qr_code.make_image(fill_color="black", back_color="white")
            qr_code_data.save('qr_code.png')
        except Exception as e:
            return JsonResponse({'message': None, 'time_taken': None, 'error': str(e)})
        
        barcode_value = request.POST.get('barcode_value', '')
        if re.match(r".*[a-z]$", barcode_value, re.IGNORECASE):
            barcode_value = barcode_value[:-1]
        barcode_data = Profile.objects.filter(barcode_value=barcode_value).first()
        if barcode_data:
            registered_events = EventRegistration.objects.filter(user=barcode_data.user)
            if registered_events:
                barcode_scan = BarcodeScan.objects.filter(user=barcode_data.user).first()
                if barcode_scan is None:
                    # start scan
                    scan = BarcodeScan(user=barcode_data.user, scan_time=timezone.now())
                    scan.save()
                    return JsonResponse({'message': 'Race start, Please enjoy your race!', 'time_taken': None, 'error': None})
                else:
                    # finish scan
                    if barcode_scan.time_taken:
                        message = f'This user {barcode_data.user.username} already participated, Time taken: {barcode_scan.time_taken} seconds. '
                        time_taken = f'Time taken: {barcode_scan.time_taken} seconds.'
                        return JsonResponse({'message': message, 'time_taken': None, 'error': None})

                    scan_time = timezone.now()
                    time_taken = (scan_time - barcode_scan.scan_time).total_seconds()
                    barcode_scan.scan_time = scan_time
                    barcode_scan.time_taken = time_taken
                    barcode_scan.save()
                    return JsonResponse({'message': None, 'time_taken': f'Time taken: {time_taken} seconds.', 'error': None})
            else:
                return JsonResponse({'message': None, 'time_taken': None, 'error': 'User not registered for any event.'})
        else:
            return JsonResponse({'message': None, 'time_taken': None, 'error': 'No user Found.'})
    else:
        return render(request, 'qr_code_scan.html')