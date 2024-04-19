from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} registered for {self.event.name}"


from django.db import models
from django.contrib.auth.models import User

class BarcodeScan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scan_time = models.DateTimeField(auto_now_add=True)
    time_taken = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Scan Time: {self.scan_time}, Time Taken: {self.time_taken} seconds"










































class QRCodeData(models.Model):
    data = models.CharField(max_length=255,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
   

    def __str__(self):
        return self.data

