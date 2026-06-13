import logging
import threading

from .services import generate_script_lines

logger = logging.getLogger(__name__)


def enqueue_script_generation(project_id):
    thread = threading.Thread(target=_run_generation, args=(project_id,), daemon=True)
    thread.start()


def _run_generation(project_id):
    try:
        generate_script_lines(project_id)
    except Exception:
        logger.exception('Script generation failed for project %s', project_id)
