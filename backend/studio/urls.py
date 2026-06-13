from django.urls import path

from .views import PodcastLineUpdateView, PodcastProjectDetailView, PodcastProjectListCreateView

urlpatterns = [
    path('projects/', PodcastProjectListCreateView.as_view(), name='studio_projects'),
    path('projects/<int:pk>/', PodcastProjectDetailView.as_view(), name='studio_project_detail'),
    path('projects/<int:project_pk>/lines/<int:pk>/', PodcastLineUpdateView.as_view(), name='studio_line_update'),
]
