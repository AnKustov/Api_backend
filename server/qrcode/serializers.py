from rest_framework import serializers

from .models import *


class QRCodeSerializer(serializers.ModelSerializer):
    guest_tg_login = serializers.SerializerMethodField()
    guest_username = serializers.SerializerMethodField()
    event_title = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = ['id', 'guest_tg_login', 'guest_username', 'event_title', 'qr_code_image']
        read_only_fields = ['id', 'guest_tg_login', 'guest_username', 'event_title', 'qr_code_image']

    def get_guest_tg_login(self, obj):
        return obj.guest.tg_login
    
    def get_guest_username(self, obj):
        return obj.guest.username     

    def get_event_title(self, obj):
        return obj.event.title
