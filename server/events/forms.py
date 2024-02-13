from django import forms
from django.utils import timezone
from .models import *


class EventReportForm(forms.ModelForm):
    class Meta:
        model = EventReport
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EventReportForm, self).__init__(*args, **kwargs)
        self.fields['event'].queryset = Event.objects.filter(date__lt=timezone.now().date())
