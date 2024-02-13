from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from .models import *


class MemberImageInline(admin.TabularInline):
    model = MemberImage
    extra = 5

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'list_latest_events', 'past_events_count', 'upcoming_events_count') 
    inlines = [MemberImageInline]
    readonly_fields = ('past_events_display', 'upcoming_events_display')
    search_fields = ('name',)

    def list_latest_events(self, obj):
        events = obj.events.all().order_by('-date')[:5] 
        event_titles = [event.title for event in events]
        if obj.events.count() > 5:
            event_titles.append("etc.")
        return ", ".join(event_titles)
    list_latest_events.short_description = 'Latest events'

    def past_events_display(self, obj):
        past_events = obj.events.filter(date__lt=now().date())
        return ", ".join([event.title for event in past_events])
    past_events_display.short_description = 'Past Events'

    def upcoming_events_display(self, obj):
        upcoming_events = obj.events.filter(date__gte=now().date())
        return ", ".join([event.title for event in upcoming_events])
    upcoming_events_display.short_description = 'Upcoming Events'

    def past_events_count(self, obj):
        return obj.events.filter(date__lt=now().date()).count()
    past_events_count.short_description = 'Past Events Count'

    def upcoming_events_count(self, obj):
        return obj.events.filter(date__gte=now().date()).count()
    upcoming_events_count.short_description = 'Upcoming Events Count'

