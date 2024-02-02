from django.db import models
from django.utils.crypto import get_random_string

from guest.models import *
from events.models import *


class Code(models.Model):
    guest = models.ForeignKey(GuestData, on_delete=models.CASCADE, related_name='codes')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='codes')
    code = models.ImageField(upload_to='qr_codes/')  # Путь для сохранения изображений QR-кодов
    identifier = models.CharField(max_length=100, unique=True, default=get_random_string)  # Уникальный идентификатор QR-кода

    def __str__(self):
        return f"QRCode for {self.guest.username} at {self.event.title}"
