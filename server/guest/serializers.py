from rest_framework import serializers
from django.utils import timezone
from datetime import date

from events.serializers import *
from qrcode.models import *
from .models import *


class NewGuestDataSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    event_title = serializers.SlugRelatedField(
        slug_field='title',
        queryset=Event.objects.filter(date__gte=timezone.now().date()),  # Только будущие события
        write_only=True
    )

    class Meta:
        model = GuestData
        fields = '__all__'
        extra_kwargs = {
            'events_attended': {'read_only': True}  # Указываем, что поле только для чтения
        }
    
    def get_age(self, obj):
        today = date.today()
        born = obj.birth_date
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    events_attended = EventSerializer(many=True, read_only=True)

    def create(self, validated_data):
        event_title = validated_data.pop('event_title', None)
        guest = GuestData.objects.create(**validated_data)

        event_info = None
        if event_title:
            try:
                event = Event.objects.get(title=event_title)
                guest.events_attended.add(event)
                event_info = EventSerializer(event).data
            except Event.DoesNotExist:
                raise serializers.ValidationError({'event_title': 'Event not found'})

        return {'guest': guest, 'event': event_info}
    

class ExistingGuestDataSerializer(serializers.ModelSerializer):
    event_title = serializers.SlugRelatedField(
        slug_field='title',
        queryset=Event.objects.filter(date__gte=timezone.now().date()),  # Только будущие события
        write_only=True
    )

    class Meta:
        model = GuestData
        fields = ['tg_login', 'event_title']

    def update(self, instance, validated_data):
        event_title = validated_data.pop('event_title', None)
        event_info = None

        if event_title:
            event = Event.objects.get(title=event_title)
            instance.events_attended.add(event)
            instance.save()
            event_info = EventSerializer(event).data

        return {'guest': instance, 'event': event_info}