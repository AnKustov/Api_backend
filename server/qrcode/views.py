from rest_framework import viewsets

from .models import *
from .serializers import *


class QRCodeViewSet(viewsets.ModelViewSet):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer
