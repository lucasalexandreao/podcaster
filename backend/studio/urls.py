from django.urls import path

from .views import CriarRoteiroPodcastView, DirectorMessageView, FinalizeProjectView, GenerationSpeedView, PodcastLineUpdateView, PodcastProjectDetailView, PodcastProjectListCreateView

urlpatterns = [
    path('projects/', PodcastProjectListCreateView.as_view(), name='studio_projects'),
    path('projects/<int:pk>/', PodcastProjectDetailView.as_view(), name='studio_project_detail'),
    path('projects/<int:pk>/speed/', GenerationSpeedView.as_view(), name='studio_speed'),
    path('projects/<int:pk>/director/', DirectorMessageView.as_view(), name='studio_director'),
    path('projects/<int:pk>/finalize/', FinalizeProjectView.as_view(), name='studio_project_finalize'),
    path('projects/<int:project_pk>/lines/<int:pk>/', PodcastLineUpdateView.as_view(), name='studio_line_update'),
    path('api/gerar-roteiro/', CriarRoteiroPodcastView.as_view(), name='gerar_roteiro'),
]
