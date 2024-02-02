import json
import qrcode
from rest_framework import viewsets, status
from rest_framework.response import Response
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.core.files.base import ContentFile
import base64
from io import BytesIO

from .models import *
from qrcode.models import *
from .serializers import *


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

        # Формирование ответа с информацией о госте и событии
        response_data = {
            'guest': NewGuestDataSerializer(result['guest']).data,
            'event': result.get('event', None)
        }

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
            # Дополнительная проверка для диагностики
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
            return Response({'message': 'Guest updated successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



        



