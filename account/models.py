from django.db import models
from django.conf import settings
from io import BytesIO
from django.core.files import File
import barcode
from barcode.writer import ImageWriter
import random
import string

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    barcode = models.ImageField(blank=True, null=True, upload_to='profile_barcodes')

    def __str__(self):
        return f'Profile of {self.user.username}'

    def generate_random_digits(self, length):
        """
        Generate random digits of specified length.
        """
        return ''.join(random.choices(string.digits, k=length))

    def save(self, *args, **kwargs):
        # Generating barcode with 12 digits
        user_id = self.user.id
        additional_digits = self.generate_random_digits(4)  # Generate 6 random digits
        barcode_data = f"{additional_digits}{user_id}"

        CODE_39 = barcode.get_barcode_class('code39')
        code = CODE_39(barcode_data, writer=ImageWriter())
        buffer = BytesIO()
        code.write(buffer)
        self.barcode.save(f'{user_id}_barcode.png', File(buffer), save=False)
        super().save(*args, **kwargs)
