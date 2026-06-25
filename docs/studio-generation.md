# Studio Generation Flow

The studio flow simulates long-running script generation without websockets or a queue dependency.

## Current Flow

1. The frontend submits `POST /api/studio/projects/`.
2. Django persists a `PodcastProject` with `status="generating"` and no lines.
3. `studio.generation.enqueue_script_generation(project_id)` starts the current local runner.
4. The runner calls `studio.services.generate_script_lines(project_id)`.
5. `generate_script_lines` builds mocked speeches and inserts one `PodcastLine` every few seconds.
6. When all lines are inserted, the project is marked `script_ready`.
7. If generation fails unexpectedly, the project is marked `failed`.
8. The frontend polls `GET /api/studio/projects/<id>/` every two seconds while status is `generating`.

## Queue Boundary

`studio/generation.py` is the queue boundary. It currently uses a daemon thread because this project only needs local mock behavior right now.

For Celery, RQ, or another queue, replace `enqueue_script_generation` with a task dispatch and have the worker task call:

```python
from studio.services import generate_script_lines

generate_script_lines(project_id)
```

Keep queue imports and broker-specific behavior out of serializers, views, and `services.py`.

## Service Rules

- `services.py` should accept plain identifiers and model data, not request objects.
- Generated output must be persisted as `PodcastLine` rows as soon as each line is available.
- Project status should be the source of truth for polling.
- The frontend should not assume a fixed number of lines; it should render whatever has been persisted.

## Current Limitations

- The daemon thread does not survive backend restarts.
- Multiple Django processes would each have their own local thread runtime.
- There is no retry mechanism beyond marking the project as `failed`.
- These limitations are acceptable for mocked local generation, but not for production generation.
