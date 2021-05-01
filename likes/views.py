from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from likes.models import Like
from likes.serializers import LikeSerializer


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = IsAuthenticated
