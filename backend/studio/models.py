from django.conf import settings
from django.db import models


class PodcastProject(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_SCRIPT_READY = 'script_ready'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SCRIPT_READY, 'Script ready'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='podcast_projects')
    topic = models.TextField()
    target_duration = models.PositiveIntegerField(default=5)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_SCRIPT_READY)
    agent1_config = models.JSONField(default=dict)
    agent2_config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.topic[:80]


class PodcastLine(models.Model):
    project = models.ForeignKey(PodcastProject, on_delete=models.CASCADE, related_name='lines')
    speaker_key = models.CharField(max_length=16)
    speaker_name = models.CharField(max_length=80)
    speaker_role = models.CharField(max_length=80)
    order = models.PositiveIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        unique_together = ('project', 'order')

    def __str__(self):
        return f'{self.speaker_name}: {self.text[:60]}'
