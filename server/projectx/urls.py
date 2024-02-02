from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from events.views import *
from member.views import *
from guest.views import *


router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'events-upcoming', UpcomingEventsViewSet, basename='events-upcoming')
router.register(r'events-past', PastEventsViewSet, basename='events-past')
router.register(r'locations', LocationViewSet)
router.register(r'location_images', LocationImageViewSet)
router.register(r'members', MemberViewSet)
router.register(r'new-registration', NewRegistrationViewSet, basename='new-registration')
router.register(r'existing-registration', ExistingRegistrationViewSet, basename='existing-registration')



urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include(router.urls)),

    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('members/<int:pk>/', MemberDetail.as_view(), name='member-detail'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
