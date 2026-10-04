# Work 014 notes

- Work 014 initialized and completed.
- Dynamic markdown parser and dashboard engine implemented at `scripts/workflow_gui.py`.
- Automated test suite in `backend/tests/test_workflow_gui.py` passing 6/6 tests.
- Standalone HTML export generated at `work/dashboard.html` and in conversation artifacts at `workflow_dashboard.html`.
- Docker service implemented:
  - `docker/workflow-gui.Dockerfile` (Python 3.12 alpine with unprivileged user `appuser` and health check)
  - `docker/compose.workflow.yaml` (standalone Compose service definition)
  - `docker/compose.yaml` (integrated alongside frontend, api, and db)
  - Volume mount: `../work:/app/work:ro` ensures live reloads when editing files in `work/` or restarting the container.
- Live server can be launched anytime via:
  - CLI: `python3 scripts/workflow_gui.py --serve --port 8088`
  - Docker Compose: `docker-compose -f docker/compose.workflow.yaml up -d`
