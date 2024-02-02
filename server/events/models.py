from django.db import models

from member.models import *


class Event(models.Model):
    LOCATION_CHOICES = [
        ('Kyiv', 'Kyiv'),
        ('Lviv', 'Lviv'),
        ('Zhytomyr', 'Zhytomyr'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(default='00:00')
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES)
    max_seats = models.PositiveIntegerField(default=9999)
    members = models.ManyToManyField(Member, related_name='events', blank=True)

    def __str__(self):
        return self.title
    
    def registered_guest_count(self):
        return self.guestdata_set.count()


class Location(models.Model):
    CITY_CHOICES = [
        ('Kyiv', 'Kyiv'),
        ('Lviv', 'Lviv'),
        ('Zhytomyr', 'Zhytomyr'),
    ]

    city = models.CharField(max_length=100, choices=CITY_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    

class LocationImage(models.Model):
    location = models.ForeignKey(Location, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='location_images/')

    def __str__(self):
        return f"Image for {self.location.name}"

