from rest_framework import viewsets, status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from guest.serializers import *
from .models import *
from .serializers import *


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class LocationImageViewSet(viewsets.ModelViewSet):
    queryset = LocationImage.objects.all()
    serializer_class = LocationImageSerializer


class LocationsByCity(APIView):
    """
    Возвращает список локаций для выбранного города.
    """

    def get(self, request, city_id):
        locations = Location.objects.filter(city__id=city_id)
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)


class EventThemaViewSet(viewsets.ModelViewSet):
    queryset = EventThema.objects.all()
    serializer_class = EventThemaSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


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
    

class EventReportViewSet(viewsets.ModelViewSet):
    queryset = EventReport.objects.all()
    serializer_class = EventReportSerializer

    @action(detail=True, methods=['post'], serializer_class=EventImagesReportSerializer)
    def add_images(self, request, pk=None):
        report = self.get_object()
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save(report=report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventImagesReportViewSet(viewsets.ModelViewSet):
    queryset = EventImagesReport.objects.all()
    serializer_class = EventImagesReportSerializer

