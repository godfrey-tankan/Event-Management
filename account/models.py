from django.db import models
from django.conf import settings
from io import BytesIO
from django.core.files import File
import qrcode
import random
import string
import barcode
from barcode.writer import ImageWriter



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    barcode = models.ImageField(blank=True, null=True, upload_to='profile_barcodes')
    barcode_value = models.CharField(max_length=16, blank=True, null=True)
    qr_code = models.ImageField(blank=True, null=True, upload_to='profile_qrcodes')
    qr_code_value = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

    def generate_random_digits(self, length):
        """
        Generate random digits of specified length.
        """
        return ''.join(random.choices(string.digits, k=length))

    def save(self, *args, **kwargs):
        if not self.barcode_value:
            # Generating barcode with 12 digits
            user_id = self.user.id
            additional_digits = self.generate_random_digits(6)  # Generate 6 random digits
            barcode_data = f"{additional_digits}{user_id}"
            self.barcode_value = barcode_data

            CODE_39 = barcode.get_barcode_class('code39')
            code = CODE_39(barcode_data, writer=ImageWriter())
            buffer = BytesIO()
            code.write(buffer)
            self.barcode.save(f'{user_id}_barcode.png', File(buffer), save=False)

        if not self.qr_code_value:
            # Generating QR code
            qr_code_data = f"{self.user.username}"
            self.qr_code_value = qr_code_data

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_code_data)
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            self.qr_code.save(f'{self.user.username}_qr_code.png', File(buffer), save=False)

        super().save(*args, **kwargs)