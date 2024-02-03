from rest_framework import viewsets
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from guest.serializers import *
from .models import *
from .serializers import *


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class LocationImageViewSet(viewsets.ModelViewSet):
    queryset = LocationImage.objects.all()
    serializer_class = LocationImageSerializer


class EventDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'pk'


class UpcomingEventsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.filter(date__gte=timezone.now().date())

class PastEventsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.filter(date__lt=timezone.now().date())
    



