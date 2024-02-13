from rest_framework import serializers
from django.utils import timezone

from member.serializers import *
from .models import *


class CitySerializer(serializers.ModelSerializer):   
    future_events = serializers.SerializerMethodField()
    class Meta:
        model = City
        fields = '__all__'

    def get_fields(self):
        fields = super(CitySerializer, self).get_fields()
        fields['locations'] = LocationSerializer(many=True, read_only=True)
        return fields
    

    def get_future_events(self, obj):
        future_events = Event.objects.filter(city=obj, date__gte=timezone.now().date())
        future_events_data = []
        for event in future_events:
            event_data = {
                "title": event.title,
                "date": event.date,
                "location": event.location.name if event.location else None, 
                "themes_titles": [theme.thema_title for theme in event.themes.all()], 
                "participation_cost": event.participation_cost,
                "members": [{"name": member.name} for member in event.members.all()]  
            }
            future_events_data.append(event_data)
        return future_events_data


class LocationImageSerializer(serializers.ModelSerializer):
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), 
        source='location'
    )

    class Meta:
        model = LocationImage
        fields = ['id', 'location_id', 'image']


class LocationSerializer(serializers.ModelSerializer):
    images = LocationImageSerializer(many=True, read_only=True)
    city = serializers.SlugRelatedField(slug_field='city_name', queryset=City.objects.all())

    class Meta:
        model = Location
        fields = ['id', 'city', 'name', 'description', 'address', 'max_seats', 'images']


def serialize_upcoming_events(events, fields):
    data = []
    for event in events:
        event_data = {}
        for field in fields:
            attribute = getattr(event, field)
            if callable(attribute):
                attribute = attribute()
            if field == 'city':
                event_data[field] = event.city.city_name
            elif field == 'location':
                event_data[field] = event.location.name
            else:
                event_data[field] = attribute
        data.append(event_data)
    return data


class EventThemaSerializer(serializers.ModelSerializer):
    past_events_count = serializers.SerializerMethodField()
    upcoming_events_count = serializers.SerializerMethodField()
    upcoming_events = serializers.SerializerMethodField()

    class Meta:
        model = EventThema
        fields = [field.name for field in model._meta.fields] + ['past_events_count', 'upcoming_events_count', 'upcoming_events']

    def get_past_events_count(self, obj):
        # Подсчет прошедших ивентов
        return Event.objects.filter(themes=obj, date__lt=timezone.now().date()).count()
    
    def get_upcoming_events_count(self, obj):
        # Подсчет будущих ивентов
        return Event.objects.filter(themes=obj, date__gte=timezone.now().date()).count()
   
    def get_upcoming_events(self, obj):
        upcoming_events = obj.events.filter(date__gte=timezone.now().date())
        fields = ['title', 'date', 'city', 'location']
        return serialize_upcoming_events(upcoming_events, fields)
        

class EventSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    members_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Member.objects.all(), 
        write_only=True, 
        required=False,
        source='members'
    )

    themes_titles = serializers.SlugRelatedField(
        many=True, 
        read_only=False,
        slug_field='thema_title', 
        queryset=EventThema.objects.all(), 
        source='themes',
        required=False
    )

    city = serializers.SlugRelatedField(
        slug_field='city_name',
        queryset=City.objects.all(),
        read_only=False
    )
    location = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Location.objects.all(),
        read_only=False
    )

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'time', 'city', 'location', 'max_seats', 'registered_guest_count', 'members', 'members_ids', 'themes_titles', 'participation_cost', 'age_restriction']

    def validate(self, data):
        """
        Проверка, что max_seats для события не превышает max_seats локации.
        """
        location = data.get('location')
        event_max_seats = data.get('max_seats')

        # Проверяем, указана ли локация и количество мест
        if location and event_max_seats:
            # Получаем max_seats из выбранной локации
            location_max_seats = Location.objects.get(id=location.id).max_seats
            
            # Сравниваем max_seats мероприятия и локации
            if event_max_seats > location_max_seats:
                raise serializers.ValidationError("The number of seats for the event exceeds the number of seats available at this location.")

        return data

    def to_representation(self, instance):
        """Модифицируем представление объекта."""
        # Сначала получаем стандартное представление модели
        ret = super().to_representation(instance)
        # Проверяем, прошло ли событие
        if instance.date < timezone.now().date():
            # Если событие прошло, добавляем информацию об отчетах
            reports = EventReport.objects.filter(event=instance)
            ret['event_reports'] = EventReportSerializer(reports, many=True, context=self.context).data
        # Если событие не прошло, информацию об отчетах добавлять не нужно
        return ret

    def get_event_reports(self, obj):
        reports = EventReport.objects.filter(event=obj)
        return EventReportSerializer(reports, many=True, context=self.context).data 

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        themes_data = validated_data.pop('themes', [])
        event = Event.objects.create(**validated_data)
        for member in members:
            event.members.add(member)
        for theme_data in themes_data:
            event.themes.add(theme_data)
        return event

    def update(self, instance, validated_data):
        if 'members' in validated_data:
            members = validated_data.pop('members')
            instance.members.clear()
            for member in members:
                instance.members.add(member)
        if 'themes' in validated_data:
            themes_data = validated_data.pop('themes')
            instance.themes.clear()
            for theme_data in themes_data:
                instance.themes.add(theme_data)
        return super().update(instance, validated_data)

    def get_registered_guest_count(self, obj):
        return obj.registered_guest_count()
    

class EventImagesReportSerializer(serializers.ModelSerializer):
    report = serializers.PrimaryKeyRelatedField(queryset=EventReport.objects.all(), write_only=True)
    class Meta:
        model = EventImagesReport
        fields = ['report', 'report_image']

    def create(self, validated_data):
        # Создание объекта изображения с привязкой к отчету
        return EventImagesReport.objects.create(**validated_data)


class EventReportSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True) 
    images = EventImagesReportSerializer(many=True, required=False, read_only=True)
    event = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.filter(date__lt=timezone.now().date()),  # Только прошедшие события
        write_only=True,
        allow_null=False,
        required=True
    )

    class Meta:
        model = EventReport
        fields = ['event', 'event_title', 'report_description', 'images']

    def create(self, validated_data):
        report = EventReport.objects.create(**validated_data)
        return report

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        for image_data in images_data:
            EventImagesReport.objects.create(report=instance, **image_data)
        return super().update(instance, validated_data)




