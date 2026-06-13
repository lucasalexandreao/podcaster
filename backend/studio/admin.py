from django.contrib import admin

from .models import PodcastLine, PodcastProject


class PodcastLineInline(admin.TabularInline):
    model = PodcastLine
    extra = 0


@admin.register(PodcastProject)
class PodcastProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'topic', 'target_duration', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('topic', 'owner__email', 'owner__username')
    inlines = (PodcastLineInline,)


@admin.register(PodcastLine)
class PodcastLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'speaker_name', 'speaker_role', 'order', 'updated_at')
    list_filter = ('speaker_role',)
    search_fields = ('text', 'speaker_name', 'project__topic')
