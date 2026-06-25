import json
import re

import anthropic
from django.conf import settings
from django.db import close_old_connections, transaction

from .models import PodcastLine, PodcastProject


def gerar_roteiro(topico, anfitriao_config, convidado_config):
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    system_prompt = f"""

        Seu papel é atuar como um roteirista de podcast, com a tarefa de escrever o roteiro em que dois agentes estarão em uma conversa.

        PERFIL DO ANFITRIÃO (Agente 1):
        - Tom: {anfitriao_config.get('tom')}
        - Personalidade: {anfitriao_config.get('personalidade')}

        PERFIL DO CONVIDADO (Agente 2):
        - Tom: {convidado_config.get('tom')}
        - Personalidade: {convidado_config.get('personalidade')}

        INSTRUÇÕES DE FORMATAÇÃO:
        - Escreva o roteiro como um diálogo direto.
        - Use as tags [Anfitrião] e [Convidado] antes das falas.
        - Inclua pequenas reações entre parênteses, como (risos), (pausa reflexiva), para ajudar na geração de áudio posterior.
        - O diálogo deve fluir naturalmente, com interrupções polidas e concordâncias, refletindo estritamente a personalidade de cada um.
    """

    user_prompt = f"Escreva o roteiro de um episódio de podcast sobre o seguinte tópico: {topico}"

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2500,
        temperature=0.7, 
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.content[0].text


def generate_script_lines(project_id):
    close_old_connections()

    try:
        project = PodcastProject.objects.get(id=project_id)

        agent1_name = project.agent1_config.get('name') or 'Anfitrião'
        agent2_name = project.agent2_config.get('name') or 'Convidado'
        agent1_tone = project.agent1_config.get('tone') or 'Neutro'
        agent2_tone = project.agent2_config.get('tone') or 'Neutro'
        agent1_traits = ', '.join(project.agent1_config.get('traits') or ['curioso'])
        agent2_traits = ', '.join(project.agent2_config.get('traits') or ['analítico'])

        system_prompt = f"""
            Seu papel é atuar como um roteirista de podcast, com a tarefa de escrever o roteiro em que dois agentes estarão em uma conversa.

            PERFIL DO ANFITRIÃO (Agente 1) - {agent1_name}:
            - Tom: {agent1_tone}
            - Personalidade: {agent1_traits}

            PERFIL DO CONVIDADO (Agente 2) - {agent2_name}:
            - Tom: {agent2_tone}
            - Personalidade: {agent2_traits}

            INSTRUÇÕES DE FORMATAÇÃO:
            - Gere o roteiro fala por fala, uma de cada vez.
            - Responda apenas com o texto da fala do personagem solicitado, sem prefixos como [Anfitrião] ou [Convidado].
            - Inclua pequenas reações entre parênteses, como (risos), (pausa reflexiva), quando apropriado.
            - O diálogo deve fluir naturalmente, refletindo estritamente a personalidade de cada um.
        """

        agents = [
            ('agent1', agent1_name, 'Anfitrião'),
            ('agent2', agent2_name, 'Convidado'),
        ]

        num_lines = max(6, project.target_duration * 2)
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        conversation_history = []

        for order in range(1, num_lines + 1):
            speaker_key, speaker_name, speaker_role = agents[(order - 1) % 2]

            if order == 1:
                user_msg = f"Inicie o episódio de podcast sobre '{project.topic}'. Escreva a fala de abertura de {speaker_name} ({speaker_role})."
            elif order == num_lines:
                user_msg = f"Esta é a última fala do episódio. Escreva o encerramento por {speaker_name} ({speaker_role})."
            else:
                user_msg = f"Continue o diálogo. Escreva a próxima fala de {speaker_name} ({speaker_role})."

            conversation_history.append({"role": "user", "content": user_msg})

            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=400,
                temperature=0.7,
                system=system_prompt,
                messages=conversation_history,
            )

            text = response.content[0].text.strip()
            conversation_history.append({"role": "assistant", "content": text})

            with transaction.atomic():
                project = PodcastProject.objects.select_for_update().get(id=project_id)
                if project.status != PodcastProject.STATUS_GENERATING:
                    return
                PodcastLine.objects.update_or_create(
                    project=project,
                    order=order,
                    defaults={
                        'speaker_key': speaker_key,
                        'speaker_name': speaker_name,
                        'speaker_role': speaker_role,
                        'text': text,
                    },
                )

        descricao, tags = gerar_metadados(project.topic)

        project.description = descricao
        project.tags = tags
        project.save()

        PodcastProject.objects.filter(id=project_id, status=PodcastProject.STATUS_GENERATING).update(
            status=PodcastProject.STATUS_SCRIPT_READY,
        )
    except Exception:
        has_lines = PodcastLine.objects.filter(project_id=project_id).exists()
        if has_lines:
            PodcastProject.objects.filter(
                id=project_id, status=PodcastProject.STATUS_GENERATING
            ).update(status=PodcastProject.STATUS_SCRIPT_READY)
        else:
            PodcastProject.objects.filter(id=project_id).update(status=PodcastProject.STATUS_FAILED)
        raise
    finally:
        close_old_connections()


def gerar_metadados(topico):
    client = anthropic.Anthropic(
        api_key=settings.ANTHROPIC_API_KEY
    )

    prompt = f"""
    Tema: {topico}

    Gere:

    1. Uma descrição curta do episódio (máx. 100 palavras)

    2. Cinco tags relacionadas

    Responda apenas em JSON:

    {{
      "descricao": "...",
      "tags": ["...", "...", "..."]
    }}
    """

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        temperature=0.4,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text = response.content[0].text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError(f'Resposta da API não contém JSON válido: {text!r}')
    dados = json.loads(match.group())

    return dados["descricao"], dados["tags"]