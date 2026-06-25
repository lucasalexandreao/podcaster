from django.db.models import Count
from .generation import enqueue_audio_generation
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from .models import DirectorMessage, PodcastLine, PodcastProject
from .serializers import PodcastLineSerializer, PodcastProjectListSerializer, PodcastProjectSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from .services import gerar_metadados, VALID_DELAYS

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


class GenerationSpeedView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk):
        project = PodcastProject.objects.filter(
            id=pk, owner=request.user, status=PodcastProject.STATUS_GENERATING
        ).first()
        if not project:
            return Response(status=status.HTTP_404_NOT_FOUND)
        delay = request.data.get('delay')
        if delay not in VALID_DELAYS:
            return Response(
                {'error': f'delay deve ser um de: {sorted(VALID_DELAYS)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project.line_delay = delay
        project.save(update_fields=['line_delay'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class DirectorMessageView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        project = PodcastProject.objects.filter(
            id=pk, owner=request.user, status=PodcastProject.STATUS_GENERATING
        ).first()
        if not project:
            return Response(status=status.HTTP_404_NOT_FOUND)
        text = request.data.get('text', '').strip()
        if not text:
            return Response({'error': 'text é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        DirectorMessage.objects.create(project=project, text=text)
        return Response(status=status.HTTP_201_CREATED)


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


class GenerateAudioView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):

        project = PodcastProject.objects.filter(
            id=pk,
            owner=request.user
        ).first()

        if not project:
            return Response(status=404)

        enqueue_audio_generation(project.id)

        return Response({
            "message": "Áudio sendo gerado"
        })