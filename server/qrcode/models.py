from django.db import models

from guest.models import *
from events.models import *


class QRCode(models.Model):
    guest = models.ForeignKey(GuestData, on_delete=models.CASCADE, related_name='qr_codes')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='qr_codes')
    qr_code_image = models.ImageField(upload_to='qr_codes/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return f"{self.guest.username} - {self.event.title}"
