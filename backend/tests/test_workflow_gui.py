import importlib.util
import json
from pathlib import Path

import pytest

import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "workflow_gui.py"
SPEC = importlib.util.spec_from_file_location("workflow_gui", SCRIPT_PATH)
workflow_gui = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = workflow_gui
SPEC.loader.exec_module(workflow_gui)


def test_parse_subtask_line_checkbox_and_owner(tmp_path):
    line_completed = "- [x] 14.1 Gemini: Interactive Agent Coordination & Task Progress GUI"
    st = workflow_gui.parse_subtask_line(line_completed, tmp_path)
    assert st is not None
    assert st.completed is True
    assert "Gemini" in st.owner
    assert "Interactive Agent Coordination" in st.title

    line_pending = "- [ ] 14.2 Codex: Reusable deployment pipeline"
    st_pending = workflow_gui.parse_subtask_line(line_pending, tmp_path)
    assert st_pending is not None
    assert st_pending.completed is False
    assert "Codex" in st_pending.owner


def test_parse_subtask_line_extracts_contract_link(tmp_path):
    task_file = tmp_path / "tasks" / "task-001.md"
    task_file.parent.mkdir(parents=True, exist_ok=True)
    task_file.write_text("# Dummy task contract\n", encoding="utf-8")

    line_with_link = "- [ ] 12.1 Root command per [task-001.md](tasks/task-001.md)"
    st = workflow_gui.parse_subtask_line(line_with_link, tmp_path)
    assert st is not None
    assert "task-001.md" in st.contract_title
    assert "tasks/task-001.md" in st.contract_path


def test_parse_work_directory_scans_active_items():
    state = workflow_gui.parse_work_directory(REPO_ROOT)
    assert state.total_work_items >= 14
    assert state.completed_items >= 1
    assert state.in_progress_items >= 1
    assert state.total_subtasks > 50
    assert 0 <= state.overall_progress_percent <= 100

    # Ensure Work 014 exists
    work_14 = next((item for item in state.items if item.id == "work-014"), None)
    assert work_14 is not None
    assert "Task Progress GUI" in work_14.title
    assert work_14.folder_name == "work-014-task-gui"


def test_generate_html_dashboard_valid_output():
    state = workflow_gui.parse_work_directory(REPO_ROOT)
    html = workflow_gui.generate_html_dashboard(state)
    assert "<!DOCTYPE html>" in html
    assert "Sulocraft Workflow & Agent Coordination" in html
    assert "work-014" in html
    assert "const DATA =" in html


def test_main_cli_builds_file(tmp_path):
    out_file = tmp_path / "test_dashboard.html"
    exit_code = workflow_gui.main(["--build", str(out_file)])
    assert exit_code == 0
    assert out_file.is_file()
    assert out_file.stat().st_size > 5000


def test_docker_workflow_gui_configuration():
    dockerfile = REPO_ROOT / "docker" / "workflow-gui.Dockerfile"
    assert dockerfile.is_file()
    df_content = dockerfile.read_text(encoding="utf-8")
    assert "FROM python:3.12-alpine" in df_content
    assert "USER appuser" in df_content
    assert "EXPOSE 8088" in df_content

    compose_file = REPO_ROOT / "docker" / "compose.workflow.yaml"
    assert compose_file.is_file()
    compose_content = compose_file.read_text(encoding="utf-8")
    assert "workflow-gui:" in compose_content
    assert "../work:/app/work:ro" in compose_content
    assert "8088" in compose_content

