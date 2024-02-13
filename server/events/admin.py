from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils.timezone import now

from events.models import *
from .forms import *


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city_name', 'location_count', 'events_count', 'future_events_count')
    search_fields = ('city_name',)
    readonly_fields = ['future_events_list', 'locations_list']

    def future_events_list(self, obj):
        future_events = Event.objects.filter(city=obj, date__gte=timezone.now().date())
        links = []
        for event in future_events:
            url = reverse('admin:events_event_change', args=[event.pk])  
            links.append(format_html('<a href="{}">{}</a>', url, event.title))
        return format_html('<br>'.join(links))
    future_events_list.short_description = "Future Events"

    def locations_list(self, obj):
        locations_html = "<ul>"
        for location in obj.locations.all():
            locations_html += f"<li>{location.name} - {location.address}</li>"
        locations_html += "</ul>"
        return mark_safe(locations_html)

    locations_list.short_description = "Locations List"

    def location_count(self, obj):
        return obj.locations.count()
    location_count.short_description = 'Location Count'

    def events_count(self, obj):
        return obj.events.count()
    events_count.short_description = 'Events Count'

    def future_events_count(self, obj):
        return Event.objects.filter(city=obj, date__gte=now().date()).count()
    future_events_count.short_description = "Future Events Count"


class LocationImageInline(admin.TabularInline):  
    model = LocationImage
    extra = 5


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'address', 'name', 'max_seats')
    inlines = [LocationImageInline,]
    search_fields = ('city', 'address', 'name')


@admin.register(EventThema)
class EventThemaAdmin(admin.ModelAdmin):
    list_display = ('thema_title', 'short_description', 'past_events_count', 'upcoming_events_count')
    readonly_fields = ('past_events', 'upcoming_events')
    search_fields = ('thema_title',)

    def short_description(self, obj):
        description = obj.description
        return description[:100] + '...' if len(description) > 100 else description
    short_description.short_description = 'Description'

    def past_events(self, obj):
        past_events = obj.events.filter(date__lt=timezone.now().date())
        return format_html_join(
            mark_safe('<br>'), 
            "{}", 
            ((event.title,) for event in past_events)
        ) or 'No past events'
    past_events.short_description = "Past Events"

    def upcoming_events(self, obj):
        upcoming_events = obj.events.filter(date__gte=timezone.now().date()).select_related('city', 'location')
        return format_html_join(
            mark_safe('<br>'), 
            "{}", 
            (
                (
                    format_html(
                        "{}, {}, {}, {}", 
                        event.title, 
                        event.city.city_name if event.city else '-', 
                        event.location.name if event.location else '-', 
                        event.location.address if event.location and hasattr(event.location, 'address') else '-'
                    ),
                ) for event in upcoming_events
            )
        ) or 'No upcoming events'

    upcoming_events.short_description = "Upcoming Events"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            past_events_count=Count('events', filter=Q(events__date__lt=timezone.now().date())),
            upcoming_events_count=Count('events', filter=Q(events__date__gte=timezone.now().date()))
        )
        return queryset

    def past_events_count(self, obj):
        return obj.past_events_count
    past_events_count.admin_order_field = 'past_events_count' 
    past_events_count.short_description = 'Past Events Count' 

    def upcoming_events_count(self, obj):
        return obj.upcoming_events_count
    upcoming_events_count.admin_order_field = 'upcoming_events_count'
    upcoming_events_count.short_description = 'Upcoming Events Count' 


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'city', 'title', 'date', 'time',
        'location', 'max_seats', 'display_members', 'display_themes',
        'participation_cost', 'age_restriction', 'registered_guest_count_display'
    )
    search_fields = ('title', 'city__city_name', 'location__name', 'themes__thema_title', 'members__name')

    def display_members(self, obj):
        """Возвращает строку с перечнем участников (или их количество)."""
        return ", ".join([member.name for member in obj.members.all()[:5]]) + (' и другие' if obj.members.count() > 5 else '')
    display_members.short_description = 'Members'

    def display_themes(self, obj):
        """Возвращает строку с перечнем тем мероприятия."""
        return ", ".join([theme.thema_title for theme in obj.themes.all()[:5]]) + (' и другие' if obj.themes.count() > 5 else '')
    display_themes.short_description = 'Themas'

    def registered_guest_count_display(self, obj):
        return obj.registered_guest_count()
    registered_guest_count_display.short_description = 'Registered Guests'


class EventImagesReportInline(admin.TabularInline):
    model = EventImagesReport
    extra = 5


@admin.register(EventReport)
class EventReportAdmin(admin.ModelAdmin):
    form = EventReportForm
    list_display = ('event', 'get_event_date')
    inlines = [EventImagesReportInline,]
    search_fields = ('event',)

    def get_event_date(self, obj):
        return obj.event.date
    get_event_date.short_description = 'Event Date' 

