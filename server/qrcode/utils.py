import segno
from django.core.files.base import ContentFile
from io import BytesIO

from .models import *


def generate_and_save_qr_code(guest, event, additional_data=None):
    # Подготовка данных для QR-кода
    qr_data = f'Guest: {guest.username}, Event: {event.title}'
    if additional_data:
        for key, value in additional_data.items():
            qr_data += f', {key}: {value}'

    qr = segno.make(qr_data, micro=False)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, kind='png', scale=5)  # Сохраняем QR-код в буфер
    qr_content = ContentFile(qr_buffer.getvalue())  # Преобразуем буфер в контент-файл Django

    # Создание или обновление объекта QRCode в базе данных
    qr_code_instance, created = QRCode.objects.get_or_create(
        guest=guest,
        event=event,
    )
    qr_code_filename = f'qr_codes/{guest.username}_{event.title}.png' 
    qr_code_instance.qr_code_image.save(qr_code_filename, qr_content, save=True)  # Сохраняем изображение в модели

    return qr_code_instance