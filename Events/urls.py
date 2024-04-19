# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-event/', views.create_event, name='create_event'),
    path('events/', views.event_list, name='event_list'),
    path('register/<int:event_id>/', views.register_for_event, name='register_for_event'),
     path('events/<int:event_id>/attendees/', views.view_event_attendees, name='view_event_attendees'),
     path('events/event/<int:event_id>/registered_users/', views.view_registered_users, name='view_registered_users'),

    path('scan/', views.scan_barcode, name='scan_barcode'),
    path('camera-scan/', views.scan_barcode, name='camera_scan_barcode'),


   
    # Add more URLs as needed
]
