from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Event
from .forms import EventForm
from django.contrib.auth.models import User


from django.http import JsonResponse
from account.models import Profile
import cv2
from pyzbar.pyzbar import decode

@staff_member_required
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

def event_list(request):
    """
    View function for displaying a list of events.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: HTTP response containing the list of events.
    """
    events = Event.objects.all()
    return render(request, 'event_list.html', {'events': events})


from django.contrib import messages

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Event

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Event, EventRegistration

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




@staff_member_required
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
    event = Event.objects.get(id=event_id)
    attendees = event.attendees.all()
    return render(request, 'event_attendees.html', {'event': event, 'attendees': attendees})


@staff_member_required
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




# # views.py
# import cv2
# from pyzbar.pyzbar import decode
# from django.http import JsonResponse
# import numpy as np

# def scan_barcode(request):
#     return render(request, 'scan.html')

# def BarcodeReader(image):
#     # Decode the barcode image
#     detectedBarcodes = decode(image)

#     # If no barcode detected, return None
#     if not detectedBarcodes:
#         return None

#     barcode_data = []
#     # Traverse through all the detected barcodes in the image
#     for barcode in detectedBarcodes:
#         # Extract barcode data
#         barcode_data.append(barcode.data.decode('utf-8'))
#         # Draw a rectangle around the barcode area
#         (x, y, w, h) = barcode.rect
#         cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5)

#     # Display the image with detected barcodes
#     cv2.imshow("Barcode Reader", image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

#     return barcode_data

# def process_barcode(request):
#     if request.method == 'POST':
#         try:
#             # Retrieve the image data from the request
#             image_data = request.POST.get('image_data')
#             # Convert base64 encoded image data to bytes
#             image_bytes = base64.b64decode(image_data.split(',')[1])
#             # Convert the bytes data to a NumPy array
#             nparr = np.frombuffer(image_bytes, np.uint8)
#             # Decode the image using OpenCV
#             image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             # Process the image to detect barcodes
#             barcode_data = BarcodeReader(image)
#             if barcode_data:
#                 # Return the detected barcode data
#                 return JsonResponse({'barcode_data': barcode_data})
#             else:
#                 return JsonResponse({'error': 'No barcode found.'})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Method not allowed.'}, status=405)




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import BarcodeScan

# views.py

import cv2
from pyzbar.pyzbar import decode
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from .models import BarcodeScan



import cv2
from pyzbar.pyzbar import decode
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import BarcodeScan

def scan_barcode(request):
    if request.method == 'POST':
        barcode_data = request.POST.get('barcode_data')
        if barcode_data:
            user = User.objects.filter(username=barcode_data).first()
            if user is None:
                message = 'User not registered for the event. Please register first.'
            else:
                message = 'Please enjoy your race!'
                # Save scanned barcode data to the database
                scan = BarcodeScan(user=user, barcode_data=barcode_data)
                scan.save()
            return JsonResponse({'message': message})
        else:
            return JsonResponse({'error': 'Barcode data not found in request.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'})
