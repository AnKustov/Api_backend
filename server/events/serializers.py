from rest_framework import serializers

from member.serializers import *
from .models import *


class EventSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    members_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Member.objects.all(), 
        write_only=True, 
        required=False,
        source='members'
    )

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'time', 'location', 'max_seats', 'registered_guest_count', 'members', 'members_ids']

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        event = Event.objects.create(**validated_data)
        for member in members:
            event.members.add(member)
        return event

    def update(self, instance, validated_data):
        if 'members' in validated_data:
            members = validated_data.pop('members')
            instance.members.clear()
            for member in members:
                instance.members.add(member)
        return super().update(instance, validated_data)

    def get_registered_guest_count(self, obj):
        return obj.registered_guest_count()
    

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

    class Meta:
        model = Location
        fields = ['id', 'city', 'name', 'description', 'images']




