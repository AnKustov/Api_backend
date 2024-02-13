from django.db import models

from member.models import *


class City(models.Model):
    city_name = models.CharField(max_length=100)

    def __str__(self):
        return self.city_name


class Location(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='locations')
    address = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    max_seats = models.PositiveIntegerField(default=9999)

    def __str__(self):
        return f"{self.name}, {self.city}"
    

class LocationImage(models.Model):
    location = models.ForeignKey(Location, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='location_images/')

    def __str__(self):
        return f"Image for {self.location.name}"


class EventThema(models.Model):
    thema_title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.thema_title


class Event(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='events', default="")
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(default='00:00')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='events')
    max_seats = models.PositiveIntegerField(default=9999)
    members = models.ManyToManyField(Member, related_name='events', blank=True)
    themes = models.ManyToManyField(EventThema, related_name='events', blank=True) 
    participation_cost = models.PositiveIntegerField(default=50)
    age_restriction = models.IntegerField(default=18)

    def __str__(self):
        return self.title
    
    def registered_guest_count(self):
        return self.guestdata_set.count()

   
class EventReport(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='report')
    report_description = models.TextField()

    def __str__(self):
        return f'Report for {self.event.title}'
    

class EventImagesReport(models.Model):
    report = models.ForeignKey(EventReport, on_delete=models.CASCADE, related_name='images')
    report_image = models.ImageField(upload_to='event_reports/', default="", blank=True)

    def __str__(self):
        return f'Image for {self.report.event.title}'


