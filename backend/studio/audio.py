import os
import re
import tempfile

from django.core.files import File
from django.conf import settings
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

from .models import PodcastProject

VOICE_REGISTRY = {
    'voz_a': 'EXAVITQu4vr4xnSDxMaL',  # Sarah  — female, professional, American
    'voz_b': 'Xb7hH8MSUJpSbSDYk0k2',  # Alice  — female, clear, British
    'voz_c': 'JBFqnCBsd6RMkjVDRZzb',  # George — male, warm storyteller, British
    'voz_d': 'CwhRBWXzGAHq8TQ4Fs17',  # Roger  — male, laid-back, American
}
_AGENT1_DEFAULT = 'voz_a'  # Sarah — female
_AGENT2_DEFAULT = 'voz_c'  # George — male

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
    return _client


def _strip_stage_directions(text: str) -> str:
    return re.sub(r'\s*\([^)]*\)', '', text).strip()


def gerar_audio_fala(texto, voice_id):
    texto = _strip_stage_directions(texto)
    audio = _get_client().text_to_speech.convert(
        voice_id=voice_id,
        text=texto,
        model_id="eleven_multilingual_v2"
    )

    arquivo = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    for chunk in audio:
        arquivo.write(chunk)
    arquivo.close()

    return arquivo.name


def juntar_audios(arquivos):
    final = AudioSegment.empty()
    pausa = AudioSegment.silent(duration=500)

    for arquivo in arquivos:
        final += AudioSegment.from_mp3(arquivo)
        final += pausa

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    final.export(output.name, format="mp3")
    return output.name


def generate_audio(project_id):
    project = PodcastProject.objects.get(id=project_id)
    project.audio_status = "generating"
    project.save(update_fields=["audio_status"])

    try:
        a1_key = project.agent1_config.get('voice', _AGENT1_DEFAULT)
        a2_key = project.agent2_config.get('voice', _AGENT2_DEFAULT)
        a1_voice = VOICE_REGISTRY.get(a1_key, VOICE_REGISTRY[_AGENT1_DEFAULT])
        a2_voice = VOICE_REGISTRY.get(a2_key, VOICE_REGISTRY[_AGENT2_DEFAULT])

        files = []
        for line in project.lines.order_by("order"):
            voice = a1_voice if line.speaker_key == "agent1" else a2_voice
            files.append(gerar_audio_fala(line.text, voice))

        final_audio = juntar_audios(files)

        for f in files:
            try:
                os.remove(f)
            except OSError:
                pass

        with open(final_audio, "rb") as f:
            project.audio_file.save(
                f"podcast_{project.id}.mp3",
                File(f),
                save=False,
            )

        project.audio_status = "ready"
        project.save()

        try:
            os.remove(final_audio)
        except OSError:
            pass

    except Exception:
        project.audio_status = "failed"
        project.save()
        raise
