from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from events.views import *
from member.views import *
from guest.views import *
from qrcode.views import *


router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'event_themas', EventThemaViewSet)
router.register(r'events', EventViewSet)
router.register(r'events-upcoming', UpcomingEventsViewSet, basename='events-upcoming')
router.register(r'events-past', PastEventsViewSet, basename='events-past')
router.register(r'event_reports', EventReportViewSet, basename='event-reports')
router.register(r'event_images_reports', EventImagesReportViewSet, basename='event-images-reports')
router.register(r'locations', LocationViewSet)
router.register(r'location_images', LocationImageViewSet)
router.register(r'members', MemberViewSet)
router.register(r'member_images', MemberImageViewSet, basename='member_images')
router.register(r'new-registration', NewRegistrationViewSet, basename='new-registration')
router.register(r'existing-registration', ExistingRegistrationViewSet, basename='existing-registration')
router.register(r'qrcodes', QRCodeViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include(router.urls)),

    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('members/<int:pk>/', MemberDetail.as_view(), name='member-detail'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
