from datetime import date, datetime, timedelta
from celery import shared_task
from django.utils import timezone

from qrcode.utils import generate_and_save_qr_code
from guest.models import GuestData
from events.models import Event
from .models import QRCode


@shared_task
def delete_expired_qr_codes():
    today = timezone.now().date()
    expired_qr_codes = QRCode.objects.filter(event__date__lt=today)
    expired_qr_codes.delete()

def calculate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

@shared_task(rate_limit='10/m')
def register_guest_for_event(guest_data_id, event_title):
    try:
        guest = GuestData.objects.get(id=guest_data_id)
        event = Event.objects.get(title=event_title)

        guest_age = calculate_age(guest.birth_date)
        
        # Проверка возрастного ограничения
        if guest_age < event.age_restriction:
            # Здесь можно отправить уведомление о невозможности регистрации из-за возрастного ограничения
            return
        
        # Проверка на закрытие регистрации
        event_start = timezone.make_aware(datetime.combine(event.date, event.time))
        if timezone.now() >= event_start - timedelta(hours=48):
            # Уведомление о закрытии регистрации
            return
        
        # Проверка на количество свободных мест
        if event.registered_guest_count() >= event.max_seats:
            # Уведомление о заполнении мест
            return
        
        # Все проверки пройдены, регистрируем гостя
        guest.events_attended.add(event)
        
        # Генерация QR-кода
        additional_data = {
            "full_name": guest.full_name,
            "tg_login": guest.tg_login,
            "event_date": event.date.strftime("%Y-%m-%d")
        }
        qr_code = generate_and_save_qr_code(guest, event, additional_data)
        
        # Отправка уведомления с QR-кодом
        # send_mail(
        #     'Registration Confirmed',
        #     f'Your registration for {event.title} is confirmed. Here is your QR code: {qr_code.qr_code_image.url}',
        #     'from@example.com',
        #     [guest.email],
        #     fail_silently=False,
        # )
        
    except GuestData.DoesNotExist:
        # Обработка ошибки, если гость не найден
        pass
    except Event.DoesNotExist:
        # Обработка ошибки, если событие не найдено
        pass