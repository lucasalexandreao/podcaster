# audio.py


import os
import tempfile

from django.core.files import File
from django.conf import settings
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

from .models import PodcastProject

client = ElevenLabs(
    api_key=settings.ELEVENLABS_API_KEY
)

AGENT1_VOICE = settings.AGENT1_VOICE
AGENT2_VOICE = settings.AGENT2_VOICE

def gerar_audio_fala(texto, voice_id):

    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=texto,
        model_id="eleven_multilingual_v2"
    )

    arquivo = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    for chunk in audio:
        arquivo.write(chunk)

    arquivo.close()

    return arquivo.name

def generate_audio(project_id):

    project = PodcastProject.objects.get(id=project_id)

    project.audio_status = "generating"
    project.save(update_fields=["audio_status"])

    try:

        files = []

        for line in project.lines.order_by("order"):

            voice = (
                AGENT1_VOICE
                if line.speaker_key == "agent1"
                else AGENT2_VOICE
            )

            path = gerar_audio_fala(
                line.text,
                voice
            )

            files.append(path)

        final_audio = juntar_audios(files)

        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass

        
        with open(final_audio, "rb") as f:

            project.audio_file.save(
                f"podcast_{project.id}.mp3",
                File(f),
                save=False
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

def juntar_audios(arquivos):

    final = AudioSegment.empty()

    pausa = AudioSegment.silent(duration=500)

    for arquivo in arquivos:
        final += AudioSegment.from_mp3(arquivo)
        final += pausa

    output = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    final.export(
        output.name,
        format="mp3"
    )

    return output.name