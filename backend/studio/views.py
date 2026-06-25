from django.db.models import Count
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from .models import PodcastLine, PodcastProject
from .serializers import PodcastLineSerializer, PodcastProjectListSerializer, PodcastProjectSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from .services import (
    gerar_roteiro,
    gerar_metadados
)

class CriarRoteiroPodcastView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            dados = request.data
            topico = dados.get('topico')
            anfitriao = dados.get('anfitriao')
            convidado = dados.get('convidado')

            if not topico or not anfitriao or not convidado:
                return Response(
                    {"erro": "Tópico, anfitrião e convidado são obrigatórios."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            roteiro = gerar_roteiro(
                topico,
                anfitriao,
                convidado
            )

            descricao, tags = gerar_metadados(topico)

            return Response({
                "mensagem": "Roteiro gerado com sucesso!",
                "roteiro": roteiro,
                "descricao": descricao,
                "tags": tags
            })

        except Exception as e:
            return Response(
                {"erro": f"Ocorreu um erro ao gerar o roteiro: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


class FinalizeProjectView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        updated = PodcastProject.objects.filter(
            id=pk,
            owner=request.user,
            status=PodcastProject.STATUS_GENERATING,
        ).update(status=PodcastProject.STATUS_SCRIPT_READY)
        if not updated:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PodcastLineUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PodcastLineSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        return PodcastLine.objects.filter(project_id=self.kwargs['project_pk'], project__owner=self.request.user)
