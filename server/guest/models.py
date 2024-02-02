from django.db import models

from events.models import *


class GuestData(models.Model):
    username = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=150, default='Just Guest')
    tg_login = models.CharField(max_length=100, unique=True)
    birth_date = models.DateField()
    company = models.TextField(blank=True)
    position = models.TextField(blank=True) 
    events_attended = models.ManyToManyField(Event, blank=True)

    def __str__(self):
        return f"{self.username}'s GuestData"

