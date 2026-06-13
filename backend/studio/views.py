from django.db.models import Count
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import PodcastLine, PodcastProject
from .serializers import PodcastLineSerializer, PodcastProjectListSerializer, PodcastProjectSerializer


class PodcastProjectListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = PodcastProject.objects.filter(owner=self.request.user)
        if self.request.method == 'GET':
            queryset = queryset.annotate(line_count=Count('lines'))
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PodcastProjectListSerializer
        return PodcastProjectSerializer


class PodcastProjectDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PodcastProjectSerializer

    def get_queryset(self):
        return PodcastProject.objects.filter(owner=self.request.user).prefetch_related('lines')


class PodcastLineUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PodcastLineSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        return PodcastLine.objects.filter(project_id=self.kwargs['project_pk'], project__owner=self.request.user)
