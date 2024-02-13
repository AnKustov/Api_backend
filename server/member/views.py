from rest_framework import viewsets
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from .models import Member
from .serializers import *


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class MemberDetail(RetrieveUpdateDestroyAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    lookup_field = 'pk'


class MemberImageViewSet(viewsets.ModelViewSet):
    queryset = MemberImage.objects.all()
    serializer_class = MemberImageSerializer