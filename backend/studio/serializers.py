from rest_framework import serializers

from .models import PodcastLine, PodcastProject


class PodcastLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodcastLine
        fields = ('id', 'speaker_key', 'speaker_name', 'speaker_role', 'order', 'text', 'created_at', 'updated_at')
        read_only_fields = ('id', 'speaker_key', 'speaker_name', 'speaker_role', 'order', 'created_at', 'updated_at')


class PodcastProjectSerializer(serializers.ModelSerializer):
    lines = PodcastLineSerializer(many=True, read_only=True)

    class Meta:
        model = PodcastProject
        fields = (
            'id',
            'topic',
            'target_duration',
            'status',
            'agent1_config',
            'agent2_config',
            'lines',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'status', 'lines', 'created_at', 'updated_at')

    def validate_topic(self, value):
        if not value.strip():
            raise serializers.ValidationError('Informe um tópico para o podcast.')
        return value.strip()

    def validate_target_duration(self, value):
        if value < 1 or value > 120:
            raise serializers.ValidationError('A duração deve estar entre 1 e 120 minutos.')
        return value

    def create(self, validated_data):
        project = PodcastProject.objects.create(owner=self.context['request'].user, **validated_data)
        PodcastLine.objects.bulk_create(build_mock_lines(project))
        return project


class PodcastProjectListSerializer(serializers.ModelSerializer):
    agents = serializers.SerializerMethodField()
    line_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PodcastProject
        fields = ('id', 'topic', 'target_duration', 'status', 'agents', 'line_count', 'created_at', 'updated_at')

    def get_agents(self, obj):
        return [
            obj.agent1_config.get('name') or 'Anfitrião',
            obj.agent2_config.get('name') or 'Convidado',
        ]


def build_mock_lines(project):
    agent1_name = project.agent1_config.get('name') or 'Anfitrião'
    agent2_name = project.agent2_config.get('name') or 'Convidado'
    agent1_tone = project.agent1_config.get('tone') or 'Neutro'
    agent2_tone = project.agent2_config.get('tone') or 'Neutro'
    agent1_traits = ', '.join(project.agent1_config.get('traits') or ['curioso'])
    agent2_traits = ', '.join(project.agent2_config.get('traits') or ['analítico'])
    topic = project.topic

    script = [
        ('agent1', agent1_name, 'Anfitrião', f'Bem-vindos ao nosso estúdio. Hoje vamos explorar: {topic}. Vou conduzir a conversa com um tom {agent1_tone.lower()} e manter o fio narrativo claro.'),
        ('agent2', agent2_name, 'Convidado', f'Perfeito. A minha leitura inicial é que {topic} merece exemplos concretos, contrapontos e uma explicação acessível. Vou trazer uma abordagem {agent2_tone.lower()}.'),
        ('agent1', agent1_name, 'Anfitrião', f'Para começar, vamos separar o tema em três partes: contexto, impacto prático e próximos passos. Os meus traços principais aqui são {agent1_traits}.'),
        ('agent2', agent2_name, 'Convidado', f'E eu vou desafiar algumas ideias para deixar o episódio mais vivo. Com traços como {agent2_traits}, a conversa deve soar natural e útil.'),
        ('agent1', agent1_name, 'Anfitrião', f'O ponto central é transformar {topic} numa história que o ouvinte consiga acompanhar do primeiro minuto até ao encerramento.'),
        ('agent2', agent2_name, 'Convidado', 'Concordo. Este é apenas um roteiro mockado, mas já deixa a estrutura pronta para revisão, edição e futura geração de áudio.'),
    ]

    return [
        PodcastLine(
            project=project,
            speaker_key=speaker_key,
            speaker_name=speaker_name,
            speaker_role=speaker_role,
            order=index,
            text=text,
        )
        for index, (speaker_key, speaker_name, speaker_role, text) in enumerate(script, start=1)
    ]
