from celery import shared_task
from django.utils import timezone
from .models import QRCode


@shared_task
def delete_expired_qr_codes():
    today = timezone.now().date()
    expired_qr_codes = QRCode.objects.filter(event__date__lt=today)
    expired_qr_codes.delete()
