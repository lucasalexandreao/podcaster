import json
import re
import time

import anthropic
from django.conf import settings
from django.db import close_old_connections, transaction

from .models import DirectorMessage, PodcastLine, PodcastProject

VALID_DELAYS = {0, 5, 10}

_SEARCH_TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for up-to-date information about the podcast topic. "
            "Call this tool before writing the very first line to understand the current state of the topic. "
            "Also call it whenever a line would benefit from a specific fact, statistic, recent development, "
            "named person, study, or data point. Prefer grounded dialogue over generic statements — "
            "if you are about to write a vague claim, search first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
                "max_results": {"type": "integer", "description": "Results to return (1–5). Default 3."},
            },
            "required": ["query"],
        },
    }
]

_MAX_TOOL_ITERATIONS = 5


def _run_search(query: str, max_results: int = 3) -> str:
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No results found."
        return "\n\n".join(
            f"{i}. {r['title']}\n{r['href']}\n{r['body']}"
            for i, r in enumerate(results, 1)
        )
    except Exception as exc:
        return f"Search unavailable: {exc}"


def _call_with_tools(client, system_prompt, messages):
    used_search = False
    for _ in range(_MAX_TOOL_ITERATIONS):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            temperature=0.7,
            system=system_prompt,
            messages=messages,
            tools=_SEARCH_TOOLS,
        )
        if response.stop_reason != "tool_use":
            return response, used_search

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "web_search":
                used_search = True
                result = _run_search(
                    query=block.input.get("query", ""),
                    max_results=int(block.input.get("max_results", 3)),
                )
            else:
                result = f"Unknown tool: {block.name}"
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "user", "content": tool_results})

    # Safety fallback: force end_turn by calling without tools
    return client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        temperature=0.7,
        system=system_prompt,
        messages=messages,
    ), used_search


def generate_script_lines(project_id):
    close_old_connections()

    try:
        project = PodcastProject.objects.get(id=project_id)

        agents = [
            ('agent1', project.agent1_config.get('name') or 'Anfitrião', 'Anfitrião',
             project.agent1_config.get('tone') or 'Neutro',
             ', '.join(project.agent1_config.get('traits') or ['curioso'])),
            ('agent2', project.agent2_config.get('name') or 'Convidado', 'Convidado',
             project.agent2_config.get('tone') or 'Neutro',
             ', '.join(project.agent2_config.get('traits') or ['analítico'])),
        ]
        other = {0: 1, 1: 0}

        base_duration = int(project.target_duration * 1.5)
        odd_duration = base_duration if base_duration % 2 != 0 else base_duration + 1

        num_lines = max(5, odd_duration)
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        conversation_history = []

        for order in range(1, num_lines + 1):
            idx = (order - 1) % 2
            speaker_key, speaker_name, speaker_role, speaker_tone, speaker_traits = agents[idx]
            _, other_name, other_role, _, _ = agents[other[idx]]

            system_prompt = f"""
                Você é {speaker_name}, o {speaker_role} de um podcast ao vivo sobre o seguinte tema:

                TEMA: {project.topic}

                QUEM VOCÊ É:
                - Tom de voz: {speaker_tone}
                - Traços de personalidade: {speaker_traits}

                Fale sempre na primeira pessoa como {speaker_name}. Não saia do personagem.
                Cada resposta sua deve avançar a discussão do tema acima — não desvie.

                USO DA PESQUISA WEB:
                - Use a ferramenta de pesquisa antes da sua primeira fala para entender o estado atual do tema.
                - Use-a também sempre que for mencionar um dado, estatística, estudo, evento recente ou pessoa real.
                - Prefira afirmações concretas e verificadas a generalidades vagas.

                FORMATAÇÃO:
                - Comece a resposta IMEDIATAMENTE com a sua fala — nenhuma palavra antes disso.
                - Proibido qualquer preâmbulo: não escreva "Claro,", "Aqui está", nem confirmações.
                - Proibido usar parênteses ou qualquer descrição de ação/emoção como (risos), (pausa), (pensativo), etc.
                - Entre 2 e 5 frases. Seja direto e natural.
            """

            # Drain pending director notes before building this turn's prompt
            pending_qs = DirectorMessage.objects.filter(project_id=project_id, consumed=False)
            pending = list(pending_qs)
            if pending:
                pending_qs.update(consumed=True)

            if order == 1:
                user_msg = (
                    f"O episódio começa agora. Pesquise o tema '{project.topic}' antes de falar. "
                    f"Abra o episódio apresentando o tema com contexto atual. ({order}/{num_lines})"
                )
            elif order == num_lines:
                user_msg = (
                    f"Última fala do episódio ({order}/{num_lines}). "
                    f"Encerre a conversa retomando o tema '{project.topic}' e deixe uma reflexão final."
                )
            else:
                user_msg = (
                    f"({order}/{num_lines}) É a sua vez, {speaker_name}. "
                    f"Responda a {other_name} e avance a discussão sobre '{project.topic}'. "
                    f"Se for citar um dado ou fato específico, pesquise antes."
                )

            if pending:
                notes = " | ".join(m.text for m in pending)
                user_msg += f"\n\n[NOTA DO DIRETOR — orienta apenas, não aparece na sua fala]: {notes}"

            conversation_history.append({"role": "user", "content": user_msg})

            response, used_search = _call_with_tools(client, system_prompt, conversation_history)

            text = next(
                (block.text for block in response.content if block.type == "text"), ""
            ).strip()
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
                        'used_web_search': used_search,
                    },
                )

            if order < num_lines:
                time.sleep(project.line_delay)

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