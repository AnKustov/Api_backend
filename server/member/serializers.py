from rest_framework import serializers
from django.utils.timezone import now

from .models import *


class MemberImageSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(),
        write_only=True
    )
    class Meta:
        model = MemberImage
        fields = ['id', 'member', 'image']
        

class MemberSerializer(serializers.ModelSerializer):
    past_events_count = serializers.SerializerMethodField()
    upcoming_events = serializers.SerializerMethodField()
    images = MemberImageSerializer(many=True, read_only=True) 

    class Meta:
        model = Member
        fields = ['id', 'name', 'description', 'images', 'past_events_count', 'upcoming_events']

    def get_past_events_count(self, obj):
        return obj.events.filter(date__lt=now().date()).count()

    def get_upcoming_events(self, obj):
        upcoming_events_qs = obj.events.filter(date__gte=now().date())
        upcoming_events = []
        for event in upcoming_events_qs:
            event_info = f"{event.title}, Themes: {', '.join([theme.thema_title for theme in event.themes.all()])}, Date: {event.date}, City: {event.city.city_name}, Location: {event.location.name}"
            upcoming_events.append(event_info)
        return upcoming_events




