from django.contrib import admin
from datetime import date
from django.utils import timezone
from django.utils.html import format_html

from .models import *
from qrcode.models import *

@admin.register(GuestData)
class GuestDataAdmin(admin.ModelAdmin):
    list_display = ('tg_login', 'username', 'birth_date', 'age_display', 'past_events_count', 'upcoming_events_count') 
    readonly_fields = ('tg_login', 'username', 'full_name', 'birth_date', 'age_display', 'past_events_display', 'upcoming_events_display') 
    search_fields = ('tg_login', 'username')

    def get_form(self, request, obj=None, **kwargs):
        form = super(GuestDataAdmin, self).get_form(request, obj, **kwargs)
        if 'events_attended' in form.base_fields:
            del form.base_fields['events_attended']
        return form

    def age_display(self, obj):
        today = date.today()
        born = obj.birth_date
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age
    age_display.short_description = 'Age'

    def past_events_display(self, obj):
        past_events = obj.events_attended.filter(date__lt=timezone.now().date())
        return ", ".join([event.title for event in past_events])
    past_events_display.short_description = 'Past Events'

    def upcoming_events_display(self, obj):
        upcoming_events = obj.events_attended.filter(date__gte=timezone.now().date())
        links = []
        for event in upcoming_events:
            qr_code = QRCode.objects.filter(guest=obj, event=event).first()
            if qr_code:
                link = format_html('<a href="{}" target="_blank">QR Code</a>', qr_code.qr_code_image.url)
                links.append(f"{event.title} ({link})")
            else:
                links.append(event.title)
        return format_html("<br>".join(links))

    upcoming_events_display.short_description = 'Upcoming Events'

    def past_events_count(self, obj):
        past_events_count = obj.events_attended.filter(date__lt=timezone.now().date()).count()
        return past_events_count
    past_events_count.short_description = 'Past Events Count'

    def upcoming_events_count(self, obj):
        upcoming_events_count = obj.events_attended.filter(date__gte=timezone.now().date()).count()
        return upcoming_events_count
    upcoming_events_count.short_description = 'Upcoming Events Count'

