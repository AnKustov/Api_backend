from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import *
from qrcode.models import *
from events.models import *
from .serializers import *
from qrcode.utils import generate_and_save_qr_code


class NewRegistrationViewSet(viewsets.ModelViewSet):
    queryset = GuestData.objects.all()
    serializer_class = NewGuestDataSerializer

    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_title = request.data.get('event_title')
        try:
            event = Event.objects.get(title=event_title)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, осталось ли более 48 часов до начала мероприятия
        event_start = timezone.make_aware(datetime.combine(event.date, event.time))
        if timezone.now() >= event_start - timedelta(hours=48):
            return Response({'error': 'Registration is closed for this event'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверка на количество свободных мест
        if event.registered_guest_count() >= event.max_seats:
            return Response({'error': 'No more seats available for this event'}, status=status.HTTP_400_BAD_REQUEST)

        result = serializer.save()

        # Генерация QR-кода
        guest = result.get('guest') 
        event = Event.objects.get(title=event_title)  
        additional_data = {
            "full_name": result['guest'].full_name,
            "tg_login": result['guest'].tg_login,
            "company": result['guest'].company,
            "position": result['guest'].position,
            "event_date": event.date.strftime("%Y-%m-%d")          
            }
        qr_code = generate_and_save_qr_code(guest, event, additional_data)

        # Формирование ответа с информацией о госте и событии
        response_data = {
            'guest': NewGuestDataSerializer(result['guest']).data,
            'qr_code_url': qr_code.qr_code_image.url
        }
        response_data['qr_code_url'] = qr_code.qr_code_image.url

        return Response(response_data, status=status.HTTP_201_CREATED)


class ExistingRegistrationViewSet(viewsets.ModelViewSet):
    queryset = GuestData.objects.all()
    serializer_class = ExistingGuestDataSerializer

    def create(self, request, *args, **kwargs):        
        tg_login = request.data.get('tg_login')
        event_title = request.data.get('event_title')

        try:
            guest = GuestData.objects.get(tg_login=tg_login)
        except GuestData.DoesNotExist:
            return Response({'error': 'Guest not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            event = Event.objects.get(title=event_title)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Проверяем, осталось ли более 48 часов до начала мероприятия
        event_start = timezone.make_aware(datetime.combine(event.date, event.time))
        if timezone.now() >= event_start - timedelta(hours=48):
            return Response({'error': 'Registration is closed for this event'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверка на количество свободных мест
        if event.registered_guest_count() >= event.max_seats:
            return Response({'error': 'No more seats available for this event'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            guest.events_attended.add(event)
            guest.save()

            # Генерация QR-кода
            additional_data = {
                "full_name": guest.full_name,
                "tg_login": guest.tg_login,
                "company": guest.company,
                "position": guest.position,
                "event_date": event.date.strftime("%Y-%m-%d")          
                }
            qr_code = generate_and_save_qr_code(guest, event, additional_data)

            response_data = {
                'message': 'Guest updated successfully',
                'qr_code_url': qr_code.qr_code_image.url  
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



        


