import time
import anthropic
from django.conf import settings
from django.db import close_old_connections, transaction

from .models import PodcastLine, PodcastProject


LINE_DELAY_SECONDS = 3

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


def build_mock_script(project):
    agent1_name = project.agent1_config.get('name') or 'Anfitrião'
    agent2_name = project.agent2_config.get('name') or 'Convidado'
    agent1_tone = project.agent1_config.get('tone') or 'Neutro'
    agent2_tone = project.agent2_config.get('tone') or 'Neutro'
    agent1_traits = ', '.join(project.agent1_config.get('traits') or ['curioso'])
    agent2_traits = ', '.join(project.agent2_config.get('traits') or ['analítico'])
    topic = project.topic

    return [
        ('agent1', agent1_name, 'Anfitrião', f'Bem-vindos ao nosso estúdio. Hoje vamos explorar: {topic}. Vou conduzir a conversa com um tom {agent1_tone.lower()} e manter o fio narrativo claro.'),
        ('agent2', agent2_name, 'Convidado', f'Perfeito. A minha leitura inicial é que {topic} merece exemplos concretos, contrapontos e uma explicação acessível. Vou trazer uma abordagem {agent2_tone.lower()}.'),
        ('agent1', agent1_name, 'Anfitrião', f'Para começar, vamos separar o tema em três partes: contexto, impacto prático e próximos passos. Os meus traços principais aqui são {agent1_traits}.'),
        ('agent2', agent2_name, 'Convidado', f'E eu vou desafiar algumas ideias para deixar o episódio mais vivo. Com traços como {agent2_traits}, a conversa deve soar natural e útil.'),
        ('agent1', agent1_name, 'Anfitrião', f'O ponto central é transformar {topic} numa história que o ouvinte consiga acompanhar do primeiro minuto até ao encerramento.'),
        ('agent2', agent2_name, 'Convidado', 'Concordo. Este é apenas um roteiro mockado, mas já deixa a estrutura pronta para revisão, edição e futura geração de áudio.'),
    ]


def generate_script_lines(project_id, line_delay=LINE_DELAY_SECONDS):
    close_old_connections()

    try:
        project = PodcastProject.objects.get(id=project_id)
        script = build_mock_script(project)

        for order, (speaker_key, speaker_name, speaker_role, text) in enumerate(script, start=1):
            time.sleep(line_delay)
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

    import json

    dados = json.loads(
        response.content[0].text
    )

    return dados["descricao"], dados["tags"]