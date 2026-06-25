from rest_framework import serializers

from .generation import enqueue_script_generation
from .models import PodcastLine, PodcastProject


class PodcastLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodcastLine
        fields = ('id', 'speaker_key', 'speaker_name', 'speaker_role', 'order', 'text', 'used_web_search', 'created_at', 'updated_at')
        read_only_fields = ('id', 'speaker_key', 'speaker_name', 'speaker_role', 'order', 'used_web_search', 'created_at', 'updated_at')


class PodcastProjectSerializer(serializers.ModelSerializer):
    lines = PodcastLineSerializer(many=True, read_only=True)
    agents = serializers.SerializerMethodField()

    class Meta:
        model = PodcastProject
        fields = (
            'id',
            'topic',
            'description',
            'tags',
            'target_duration',
            'line_delay',
            'status',
            'agents',
            'lines',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'id',
            'description',
            'tags',
            'status',
            'lines',
            'created_at',
            'updated_at',
        )

    def get_agents(self, obj):
        return [
            obj.agent1_config.get('name') or 'Anfitrião',
            obj.agent2_config.get('name') or 'Convidado',
        ]

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
        enqueue_script_generation(project.id)
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
