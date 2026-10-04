#!/usr/bin/env python3
"""Sulocraft Workflow & Agent Coordination GUI Dashboard.

Parses work/INDEX.md, work/work-*/ directory structures, tasks.md, coordination.md,
and task contracts, and renders an interactive web GUI dashboard.
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import re
import socketserver
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = REPO_ROOT / "work"


@dataclass
class TaskContract:
    path: str
    filename: str
    title: str = ""
    owner: str = ""
    status: str = ""
    objective: str = ""
    scope_in: list[str] = field(default_factory=list)
    scope_out: list[str] = field(default_factory=list)
    acceptance_checks: list[str] = field(default_factory=list)


@dataclass
class SubTask:
    id: str
    title: str
    completed: bool
    owner: str = ""
    contract_path: str = ""
    contract_title: str = ""


@dataclass
class WorkItem:
    id: str
    number: int
    title: str
    status: str  # "Completed", "In Progress", "Pending", "Blocked"
    folder_name: str
    relative_path: str
    goal: str = ""
    current_owner: str = ""
    active_handoffs: str = ""
    handoff_state: str = ""
    subtasks: list[SubTask] = field(default_factory=list)
    decisions: list[dict[str, str]] = field(default_factory=list)
    contracts: list[TaskContract] = field(default_factory=list)
    total_subtasks: int = 0
    completed_subtasks: int = 0
    progress_percent: int = 0


@dataclass
class WorkflowState:
    generated_at: str
    total_work_items: int
    completed_items: int
    in_progress_items: int
    pending_items: int
    blocked_items: int
    total_subtasks: int
    completed_subtasks: int
    overall_progress_percent: int
    items: list[WorkItem] = field(default_factory=list)


def parse_subtask_line(line: str, work_folder: Path) -> SubTask | None:
    match = re.match(r"^[-*]\s+\[([ xX])\]\s*(.*)$", line.strip())
    if not match:
        return None

    completed = match.group(1).lower() == "x"
    raw_text = match.group(2).strip()

    # Extract contract link if present: [Title](relative/path.md)
    contract_path = ""
    contract_title = ""
    link_match = re.search(r"\[([^\]]+)\]\(([^)]+\.md)\)", raw_text)
    if link_match:
        contract_title = link_match.group(1)
        rel_contract = link_match.group(2)
        # Normalize relative path to work_folder
        resolved_contract = (work_folder / rel_contract).resolve()
        try:
            contract_path = str(resolved_contract.relative_to(REPO_ROOT))
        except ValueError:
            contract_path = rel_contract

    # Extract owner if specified (e.g., "Gemini:", "Codex:", "Owner + Codex:")
    owner = ""
    owner_match = re.search(r"(?:^|\s)(Gemini|Codex|GPT|Owner)(?:\s*\+\s*(Gemini|Codex|GPT|Owner))?:", raw_text)
    if owner_match:
        owner = owner_match.group(0).rstrip(":")

    # Clean display title (strip markdown link formatting for simple display)
    display_title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw_text).strip()

    # Generate a simple subtask id
    subtask_id = re.sub(r"[^a-zA-Z0-9_-]", "-", display_title[:32]).strip("-")

    return SubTask(
        id=subtask_id,
        title=display_title,
        completed=completed,
        owner=owner,
        contract_path=contract_path,
        contract_title=contract_title,
    )


def parse_task_contract(contract_file: Path) -> TaskContract:
    contract = TaskContract(
        path=str(contract_file.relative_to(REPO_ROOT)),
        filename=contract_file.name,
    )
    if not contract_file.is_file():
        return contract

    content = contract_file.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    current_section = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            contract.title = stripped[2:].strip()
            continue

        if stripped.startswith("**Owner:**"):
            contract.owner = stripped.replace("**Owner:**", "").strip()
            continue

        if stripped.startswith("**Status:**"):
            contract.status = stripped.replace("**Status:**", "").strip()
            continue

        if stripped.startswith("## "):
            current_section = stripped[3:].strip().lower()
            continue

        if current_section == "objective" and stripped and not stripped.startswith("#"):
            if not contract.objective:
                contract.objective = stripped
            else:
                contract.objective += " " + stripped

        if current_section == "scope":
            if stripped.startswith("- In scope:") or stripped.startswith("- In scope"):
                continue
            elif stripped.startswith("- Out of scope:") or stripped.startswith("- Out of scope"):
                current_section = "scope_out"
            elif stripped.startswith("- ") or stripped.startswith("* "):
                contract.scope_in.append(stripped[2:].strip())

        if current_section == "scope_out":
            if stripped.startswith("- ") or stripped.startswith("* "):
                contract.scope_out.append(stripped[2:].strip())

        if "acceptance" in current_section:
            if stripped.startswith("- [ ]") or stripped.startswith("- [x]"):
                contract.acceptance_checks.append(stripped)

    return contract


def parse_work_directory(repo_root: Path = REPO_ROOT) -> WorkflowState:
    work_dir = repo_root / "work"
    index_file = work_dir / "INDEX.md"

    # 1. Parse high-level work items from INDEX.md
    index_items: dict[str, dict[str, str]] = {}
    if index_file.is_file():
        index_content = index_file.read_text(encoding="utf-8", errors="replace")
        for line in index_content.splitlines():
            # Pattern: - **Work 001 — Title** · Status · [work folder](work-001-admin-dashboard/)
            match = re.search(
                r"-\s+\*\*Work\s+(\d+)\s+[—–-]\s+([^*]+)\*\*\s+·\s+([^·]+?)\s+·\s+\[work folder\]\(([^)]+)\)",
                line,
            )
            if match:
                num_str, title, status_raw, folder = match.groups()
                item_id = f"work-{int(num_str):03d}"
                # Normalize status
                status = "Pending"
                if "Completed" in status_raw:
                    status = "Completed"
                elif "In Progress" in status_raw:
                    status = "In Progress"
                elif "Blocked" in status_raw:
                    status = "Blocked"

                index_items[item_id] = {
                    "number": int(num_str),
                    "title": title.strip(),
                    "status": status,
                    "folder": folder.strip("/"),
                }

    # 2. Discover work folders on disk
    work_items: list[WorkItem] = []
    discovered_dirs = sorted([d for d in work_dir.iterdir() if d.is_dir() and d.name.startswith("work-")])

    for folder in discovered_dirs:
        folder_match = re.match(r"work-(\d+)", folder.name)
        if not folder_match:
            continue
        num = int(folder_match.group(1))
        item_id = f"work-{num:03d}"

        index_info = index_items.get(item_id, {})
        title = index_info.get("title", folder.name.replace("-", " ").title())
        status = index_info.get("status", "Pending")

        # Parse README.md for Goal
        goal = ""
        readme_path = folder / "README.md"
        if readme_path.is_file():
            readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
            # Look for ## Goal or Objective
            goal_match = re.search(r"##\s+(?:Goal|Objective)\s*\n+([^#\n][^\n]+)", readme_text)
            if goal_match:
                goal = goal_match.group(1).strip()
            else:
                first_lines = [l.strip() for l in readme_text.splitlines() if l.strip() and not l.startswith("#")]
                if first_lines:
                    goal = first_lines[0]

        # Parse coordination.md for Owner and Handoff State
        current_owner = ""
        active_handoffs = ""
        handoff_state = ""
        coord_path = folder / "coordination.md"
        if coord_path.is_file():
            coord_text = coord_path.read_text(encoding="utf-8", errors="replace")
            owner_m = re.search(r"\*\*Current owner:\*\*\s*([^\n]+)", coord_text)
            if owner_m:
                current_owner = owner_m.group(1).strip()
            handoff_m = re.search(r"\*\*Active cross-agent handoffs:\*\*\s*([^\n]+)", coord_text)
            if handoff_m:
                active_handoffs = handoff_m.group(1).strip()
            state_m = re.search(r"\*\*Handoff state:\*\*\s*([^\n]+)", coord_text)
            if state_m:
                handoff_state = state_m.group(1).strip()

        # Parse tasks.md for Subtasks
        subtasks: list[SubTask] = []
        tasks_path = folder / "tasks.md"
        if tasks_path.is_file():
            tasks_text = tasks_path.read_text(encoding="utf-8", errors="replace")
            for line in tasks_text.splitlines():
                subtask = parse_subtask_line(line, folder)
                if subtask:
                    subtasks.append(subtask)

        # Parse decisions.md
        decisions: list[dict[str, str]] = []
        decisions_path = folder / "decisions.md"
        if decisions_path.is_file():
            dec_text = decisions_path.read_text(encoding="utf-8", errors="replace")
            dec_matches = re.findall(r"##\s+([^\n]+)\n+([\s\S]*?)(?=\n##|\Z)", dec_text)
            for d_title, d_body in dec_matches:
                decisions.append({
                    "title": d_title.strip(),
                    "body": d_body.strip()[:300] + ("..." if len(d_body.strip()) > 300 else ""),
                })

        # Parse task contracts under tasks/
        contracts: list[TaskContract] = []
        tasks_subdir = folder / "tasks"
        if tasks_subdir.is_dir():
            for c_file in sorted(tasks_subdir.glob("*.md")):
                if c_file.name != "README.md":
                    contracts.append(parse_task_contract(c_file))

        total_sub = len(subtasks)
        completed_sub = sum(1 for st in subtasks if st.completed)
        progress_pct = round((completed_sub / total_sub * 100)) if total_sub > 0 else (100 if status == "Completed" else 0)

        work_items.append(
            WorkItem(
                id=item_id,
                number=num,
                title=title,
                status=status,
                folder_name=folder.name,
                relative_path=str(folder.relative_to(repo_root)),
                goal=goal,
                current_owner=current_owner,
                active_handoffs=active_handoffs,
                handoff_state=handoff_state,
                subtasks=subtasks,
                decisions=decisions,
                contracts=contracts,
                total_subtasks=total_sub,
                completed_subtasks=completed_sub,
                progress_percent=progress_pct,
            )
        )

    # Calculate global project stats
    total_items = len(work_items)
    completed_items = sum(1 for item in work_items if item.status == "Completed")
    in_progress_items = sum(1 for item in work_items if item.status == "In Progress")
    pending_items = sum(1 for item in work_items if item.status == "Pending")
    blocked_items = sum(1 for item in work_items if item.status == "Blocked")

    global_total_sub = sum(item.total_subtasks for item in work_items)
    global_completed_sub = sum(item.completed_subtasks for item in work_items)
    overall_progress = (
        round((global_completed_sub / global_total_sub * 100))
        if global_total_sub > 0
        else round((completed_items / total_items * 100) if total_items > 0 else 0)
    )

    return WorkflowState(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        total_work_items=total_items,
        completed_items=completed_items,
        in_progress_items=in_progress_items,
        pending_items=pending_items,
        blocked_items=blocked_items,
        total_subtasks=global_total_sub,
        completed_subtasks=global_completed_sub,
        overall_progress_percent=overall_progress,
        items=work_items,
    )


def generate_html_dashboard(state: WorkflowState) -> str:
    """Generate standalone interactive HTML dashboard."""
    state_json = json.dumps(asdict(state), indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sulocraft Workflow & Agent Coordination Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      --background: #090d16;
      --card: #111827;
      --card-hover: #1f2937;
      --border: #1f2937;
      --foreground: #f3f4f6;
      --muted-foreground: #9ca3af;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
    }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .custom-scrollbar::-webkit-scrollbar-track {{
      background: rgba(0, 0, 0, 0.1);
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: rgba(156, 163, 175, 0.3);
      border-radius: 3px;
    }}
  </style>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] min-h-screen antialiased flex flex-col">

  <!-- Header Banner -->
  <header class="bg-[var(--card)] border-b border-[var(--border)] sticky top-0 z-30 shadow-md">
    <div class="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-inner">
          🧶
        </div>
        <div>
          <h1 class="text-lg font-bold tracking-tight text-[var(--foreground)] flex items-center gap-2">
            Sulocraft Workflow & Coordination
            <span class="text-xs font-normal px-2 py-0.5 rounded-full bg-blue-900/60 text-blue-300 border border-blue-700/50">Live</span>
          </h1>
          <p class="text-xs text-[var(--muted-foreground)]">Tracking {state.total_work_items} work items across Gemini, Codex & Owner</p>
        </div>
      </div>

      <!-- Overall Progress Stat -->
      <div class="flex items-center gap-6">
        <div class="flex items-center gap-3">
          <div class="text-right">
            <div class="text-xs font-medium text-[var(--muted-foreground)]">Overall Progress</div>
            <div class="text-sm font-bold text-blue-400">{state.overall_progress_percent}% ({state.completed_subtasks}/{state.total_subtasks} subtasks)</div>
          </div>
          <div class="w-24 bg-gray-800 rounded-full h-2.5 overflow-hidden border border-gray-700">
            <div class="bg-blue-500 h-2.5 rounded-full transition-all duration-500" style="width: {state.overall_progress_percent}%;"></div>
          </div>
        </div>

        <button onclick="location.reload()" title="Refresh live data" class="px-3 py-1.5 rounded-md bg-[var(--card-hover)] hover:bg-gray-700 text-xs font-medium border border-[var(--border)] transition flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          Sync
        </button>
      </div>
    </div>
  </header>

  <!-- Metrics Bar -->
  <div class="bg-[var(--card)]/50 border-b border-[var(--border)] py-2.5">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 text-center">
      <div class="p-2 rounded-lg bg-[var(--card)] border border-[var(--border)]">
        <div class="text-xs text-[var(--muted-foreground)]">Total Items</div>
        <div class="text-lg font-bold text-white">{state.total_work_items}</div>
      </div>
      <div class="p-2 rounded-lg bg-emerald-950/40 border border-emerald-800/40">
        <div class="text-xs text-emerald-400">Completed</div>
        <div class="text-lg font-bold text-emerald-300">{state.completed_items}</div>
      </div>
      <div class="p-2 rounded-lg bg-blue-950/40 border border-blue-800/40">
        <div class="text-xs text-blue-400">In Progress</div>
        <div class="text-lg font-bold text-blue-300">{state.in_progress_items}</div>
      </div>
      <div class="p-2 rounded-lg bg-amber-950/40 border border-amber-800/40">
        <div class="text-xs text-amber-400">Pending</div>
        <div class="text-lg font-bold text-amber-300">{state.pending_items}</div>
      </div>
      <div class="p-2 rounded-lg bg-gray-900 border border-[var(--border)] col-span-2 sm:col-span-4 lg:col-span-1">
        <div class="text-xs text-[var(--muted-foreground)]">Completed Subtasks</div>
        <div class="text-lg font-bold text-gray-200">{state.completed_subtasks} / {state.total_subtasks}</div>
      </div>
    </div>
  </div>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8 flex-1 flex flex-col w-full">
    
    <!-- Controls Toolbar (Search & Filter Pills) -->
    <div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 mb-5">
      <!-- Filter Pills -->
      <div class="flex items-center gap-1.5 flex-wrap">
        <button onclick="setFilter('ALL')" id="filter-ALL" class="filter-btn px-3 py-1.5 rounded-full text-xs font-medium bg-blue-600 text-white transition shadow-sm">
          All ({state.total_work_items})
        </button>
        <button onclick="setFilter('IN_PROGRESS')" id="filter-IN_PROGRESS" class="filter-btn px-3 py-1.5 rounded-full text-xs font-medium bg-[var(--card)] hover:bg-[var(--card-hover)] text-[var(--muted-foreground)] border border-[var(--border)] transition">
          In Progress ({state.in_progress_items})
        </button>
        <button onclick="setFilter('COMPLETED')" id="filter-COMPLETED" class="filter-btn px-3 py-1.5 rounded-full text-xs font-medium bg-[var(--card)] hover:bg-[var(--card-hover)] text-[var(--muted-foreground)] border border-[var(--border)] transition">
          Completed ({state.completed_items})
        </button>
        <button onclick="setFilter('PENDING')" id="filter-PENDING" class="filter-btn px-3 py-1.5 rounded-full text-xs font-medium bg-[var(--card)] hover:bg-[var(--card-hover)] text-[var(--muted-foreground)] border border-[var(--border)] transition">
          Pending ({state.pending_items})
        </button>
      </div>

      <!-- Search Input -->
      <div class="relative w-full md:w-72">
        <input
          type="text"
          id="search-input"
          oninput="handleSearch(this.value)"
          placeholder="Search work, subtasks, agent..."
          class="w-full bg-[var(--card)] border border-[var(--border)] rounded-lg px-3 py-1.5 pl-9 text-xs text-[var(--foreground)] placeholder-[var(--muted-foreground)] focus:outline-none focus:border-blue-500 transition"
        />
        <svg class="w-4 h-4 text-gray-500 absolute left-2.5 top-2.5 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
    </div>

    <!-- 2-Column Responsive Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 flex-1 min-h-0">
      
      <!-- Left Column: Work Items List (5 cols) -->
      <div class="lg:col-span-5 flex flex-col h-[750px] bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div class="px-4 py-3 border-b border-[var(--border)] bg-gray-900/40 flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">Work Items</span>
          <span id="items-count-badge" class="text-xs bg-gray-800 px-2 py-0.5 rounded text-gray-300">Showing {state.total_work_items}</span>
        </div>
        <div id="work-items-list" class="flex-1 overflow-y-auto divide-y divide-[var(--border)] custom-scrollbar">
          <!-- Dynamically populated by JS -->
        </div>
      </div>

      <!-- Right Column: Detail Pane (7 cols) -->
      <div class="lg:col-span-7 flex flex-col h-[750px] bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div id="detail-header" class="px-5 py-4 border-b border-[var(--border)] bg-gray-900/40 flex items-center justify-between">
          <!-- Dynamically populated header -->
        </div>
        <div id="detail-body" class="flex-1 overflow-y-auto p-5 custom-scrollbar space-y-6">
          <!-- Dynamically populated content -->
        </div>
      </div>

    </div>

  </main>

  <!-- Contract Modal -->
  <div id="contract-modal" class="fixed inset-0 z-50 hidden bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-5 py-3.5 border-b border-[var(--border)] bg-gray-900/50 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-base">📄</span>
          <h3 id="modal-title" class="text-sm font-bold text-white truncate max-w-md">Task Contract</h3>
        </div>
        <button onclick="closeModal()" class="text-gray-400 hover:text-white p-1 rounded-md hover:bg-gray-800 transition">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
      <div id="modal-body" class="p-5 overflow-y-auto space-y-4 custom-scrollbar text-xs text-gray-300">
        <!-- Contract contents -->
      </div>
      <div class="px-5 py-3 border-t border-[var(--border)] bg-gray-900/30 flex justify-end">
        <button onclick="closeModal()" class="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium transition">Close</button>
      </div>
    </div>
  </div>

  <footer class="border-t border-[var(--border)] py-3 text-center text-xs text-[var(--muted-foreground)]">
    Sulocraft Multi-Agent Coordination • Last scanned: {state.generated_at}
  </footer>

  <script>
    const DATA = {state_json};
    let currentFilter = 'ALL';
    let searchQuery = '';
    let selectedItemId = DATA.items.length > 0 ? DATA.items[0].id : null;

    function getStatusBadge(status) {{
      switch(status) {{
        case 'Completed':
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950 text-emerald-300 border border-emerald-700/50">Completed</span>';
        case 'In Progress':
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-950 text-blue-300 border border-blue-700/50">In Progress</span>';
        case 'Pending':
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-950 text-amber-300 border border-amber-700/50">Pending</span>';
        case 'Blocked':
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-red-950 text-red-300 border border-red-700/50">Blocked</span>';
        default:
          return '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-gray-800 text-gray-300 border border-gray-700">' + status + '</span>';
      }}
    }}

    function filterItems() {{
      return DATA.items.filter(item => {{
        // Filter by Status
        if (currentFilter === 'COMPLETED' && item.status !== 'Completed') return false;
        if (currentFilter === 'IN_PROGRESS' && item.status !== 'In Progress') return false;
        if (currentFilter === 'PENDING' && item.status !== 'Pending') return false;
        if (currentFilter === 'BLOCKED' && item.status !== 'Blocked') return false;

        // Filter by Search Query
        if (searchQuery) {{
          const q = searchQuery.toLowerCase();
          const matchTitle = item.title.toLowerCase().includes(q);
          const matchId = item.id.toLowerCase().includes(q);
          const matchOwner = (item.current_owner || '').toLowerCase().includes(q);
          const matchGoal = (item.goal || '').toLowerCase().includes(q);
          const matchSubtask = item.subtasks.some(st => st.title.toLowerCase().includes(q));
          if (!matchTitle && !matchId && !matchOwner && !matchGoal && !matchSubtask) return false;
        }}

        return true;
      }});
    }}

    function setFilter(filter) {{
      currentFilter = filter;
      document.querySelectorAll('.filter-btn').forEach(btn => {{
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('bg-[var(--card)]', 'text-[var(--muted-foreground)]');
      }});
      const activeBtn = document.getElementById('filter-' + filter);
      if (activeBtn) {{
        activeBtn.classList.remove('bg-[var(--card)]', 'text-[var(--muted-foreground)]');
        activeBtn.classList.add('bg-blue-600', 'text-white');
      }}
      renderList();
    }}

    function handleSearch(val) {{
      searchQuery = val.trim();
      renderList();
    }}

    function selectItem(id) {{
      selectedItemId = id;
      renderList();
      renderDetail();
    }}

    function renderList() {{
      const items = filterItems();
      const listEl = document.getElementById('work-items-list');
      document.getElementById('items-count-badge').textContent = `Showing ${{items.length}}`;

      if (items.length === 0) {{
        listEl.innerHTML = `
          <div class="p-8 text-center text-xs text-gray-500">
            No work items match the selected filter or search query.
          </div>
        `;
        return;
      }}

      // If selected item is not in filtered list, select first available
      if (!items.some(i => i.id === selectedItemId)) {{
        selectedItemId = items[0].id;
        renderDetail();
      }}

      listEl.innerHTML = items.map(item => {{
        const isSelected = item.id === selectedItemId;
        return `
          <div
            onclick="selectItem('${{item.id}}')"
            class="p-3.5 cursor-pointer transition flex flex-col gap-2 ${{
              isSelected
                ? 'bg-blue-950/40 border-l-4 border-blue-500 pl-3'
                : 'hover:bg-gray-800/50'
            }}"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2 truncate">
                <span class="font-mono text-xs font-bold text-gray-400">#${{String(item.number).padStart(3, '0')}}</span>
                <span class="text-xs font-semibold text-gray-100 truncate">${{item.title}}</span>
              </div>
              <div>${{getStatusBadge(item.status)}}</div>
            </div>

            <div class="flex items-center justify-between text-[11px] text-gray-400">
              <span class="flex items-center gap-1 truncate max-w-[180px]">
                <span class="text-gray-500">Owner:</span>
                <span class="font-medium text-gray-300 truncate">${{item.current_owner || 'Unassigned'}}</span>
              </span>
              <span>${{item.completed_subtasks}}/${{item.total_subtasks}} tasks (${{item.progress_percent}}%)</span>
            </div>

            <!-- Mini Progress Bar -->
            <div class="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
              <div class="bg-blue-500 h-1.5 rounded-full transition-all" style="width: ${{item.progress_percent}}%;"></div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function renderDetail() {{
      const item = DATA.items.find(i => i.id === selectedItemId);
      const headerEl = document.getElementById('detail-header');
      const bodyEl = document.getElementById('detail-body');

      if (!item) {{
        headerEl.innerHTML = '<span class="text-xs text-gray-400">Select an item</span>';
        bodyEl.innerHTML = '<div class="text-center text-xs text-gray-500 py-12">No work item selected.</div>';
        return;
      }}

      // Render Header
      headerEl.innerHTML = `
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-2">
            <span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-gray-800 text-gray-300">Work ${{String(item.number).padStart(3, '0')}}</span>
            <h2 class="text-sm font-bold text-white truncate max-w-md">${{item.title}}</h2>
          </div>
          <span class="text-[11px] text-gray-400 font-mono">${{item.relative_path}}</span>
        </div>
        <div class="flex items-center gap-3">
          ${{getStatusBadge(item.status)}}
        </div>
      `;

      // Render Subtasks
      const subtasksHtml = item.subtasks.length === 0
        ? '<p class="text-xs text-gray-500 italic">No checklist subtasks declared in tasks.md.</p>'
        : `
          <div class="space-y-2">
            ${{item.subtasks.map(st => `
              <div class="flex items-start justify-between gap-3 p-2.5 rounded-lg border ${{
                st.completed ? 'bg-emerald-950/20 border-emerald-900/40 text-gray-300' : 'bg-gray-800/40 border-gray-700/50 text-gray-200'
              }}">
                <div class="flex items-start gap-2.5">
                  <span class="mt-0.5 text-xs ${{st.completed ? 'text-emerald-400 font-bold' : 'text-gray-500'}}">
                    ${{st.completed ? '☑' : '☐'}}
                  </span>
                  <div class="flex flex-col">
                    <span class="text-xs font-medium ${{st.completed ? 'line-through text-gray-400' : ''}}">${{st.title}}</span>
                    ${{st.owner ? `<span class="text-[10px] text-blue-400 font-semibold mt-0.5">Assigned: ${{st.owner}}</span>` : ''}}
                  </div>
                </div>
                ${{st.contract_path ? `
                  <button onclick="viewContract('${{item.id}}', '${{st.contract_path}}')" class="shrink-0 px-2 py-1 rounded bg-blue-900/40 hover:bg-blue-800 text-blue-300 text-[10px] font-medium border border-blue-700/50 transition">
                    View Contract
                  </button>
                ` : ''}}
              </div>
            `).join('')}}
          </div>
        `;

      // Render Contracts List
      const contractsHtml = item.contracts.length === 0
        ? ''
        : `
          <div class="pt-4 border-t border-[var(--border)]">
            <h4 class="text-xs font-bold uppercase tracking-wider text-[var(--muted-foreground)] mb-3 flex items-center gap-1.5">
              <span>📄</span> Task Contracts (${{item.contracts.length}})
            </h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              ${{item.contracts.map(c => `
                <div onclick="showModal('${{escapeHtml(c.title || c.filename)}}', '${{escapeHtml(c.objective || 'No objective specified.')}}', '${{escapeHtml(c.status || '')}}', '${{escapeHtml(c.owner || '')}}', ${{JSON.stringify(c.acceptance_checks).replace(/"/g, '&quot;')}})" class="p-2.5 rounded-lg bg-[var(--card-hover)] border border-[var(--border)] hover:border-blue-500 cursor-pointer transition">
                  <div class="text-xs font-semibold text-white truncate">${{c.title || c.filename}}</div>
                  <div class="text-[10px] text-gray-400 mt-1 flex items-center justify-between">
                    <span>${{c.owner || 'Unassigned'}}</span>
                    <span class="text-blue-400">Inspect →</span>
                  </div>
                </div>
              `).join('')}}
            </div>
          </div>
        `;

      // Render Decisions
      const decisionsHtml = item.decisions.length === 0
        ? ''
        : `
          <div class="pt-4 border-t border-[var(--border)]">
            <h4 class="text-xs font-bold uppercase tracking-wider text-[var(--muted-foreground)] mb-3 flex items-center gap-1.5">
              <span>⚖️</span> Recorded Decisions (${{item.decisions.length}})
            </h4>
            <div class="space-y-2">
              ${{item.decisions.map(d => `
                <div class="p-2.5 rounded-lg bg-gray-900/60 border border-[var(--border)]">
                  <div class="text-xs font-bold text-gray-200">${{d.title}}</div>
                  <div class="text-[11px] text-gray-400 mt-1 whitespace-pre-line">${{d.body}}</div>
                </div>
              `).join('')}}
            </div>
          </div>
        `;

      // Assemble Detail Body
      bodyEl.innerHTML = `
        <!-- Objective Card -->
        <div class="bg-gray-900/60 border border-[var(--border)] rounded-xl p-4">
          <div class="text-xs font-bold uppercase tracking-wider text-[var(--muted-foreground)] mb-1.5">Objective / Goal</div>
          <p class="text-xs text-gray-200 leading-relaxed">${{item.goal || 'No explicit goal documented in README.'}}</p>
        </div>

        <!-- Coordination & Handoff Card -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="bg-gray-900/40 border border-[var(--border)] rounded-xl p-3.5">
            <div class="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Current Owner</div>
            <div class="text-xs font-semibold text-blue-300">${{item.current_owner || 'Unassigned / Pending'}}</div>
          </div>
          <div class="bg-gray-900/40 border border-[var(--border)] rounded-xl p-3.5">
            <div class="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Handoff State</div>
            <div class="text-xs font-semibold text-gray-200 truncate">${{item.handoff_state || 'No active handoff'}}</div>
          </div>
        </div>

        <!-- Subtasks Section -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-[var(--muted-foreground)] flex items-center gap-1.5">
              <span>☑</span> Subtasks & Checklist (${{item.completed_subtasks}}/${{item.total_subtasks}})
            </h4>
            <span class="text-xs font-semibold text-blue-400">${{item.progress_percent}}% Complete</span>
          </div>
          ${{subtasksHtml}}
        </div>

        ${{contractsHtml}}
        ${{decisionsHtml}}
      `;
    }}

    function viewContract(itemId, contractPath) {{
      const item = DATA.items.find(i => i.id === itemId);
      if (!item) return;
      const contract = item.contracts.find(c => c.path === contractPath || contractPath.endsWith(c.filename));
      if (contract) {{
        showModal(contract.title || contract.filename, contract.objective, contract.status, contract.owner, contract.acceptance_checks);
      }} else {{
        alert('Contract file: ' + contractPath);
      }}
    }}

    function showModal(title, objective, status, owner, acceptanceChecks) {{
      document.getElementById('modal-title').textContent = title;
      const bodyEl = document.getElementById('modal-body');
      
      const checksHtml = (acceptanceChecks && acceptanceChecks.length > 0)
        ? `<div class="mt-4 pt-3 border-t border-[var(--border)]">
             <div class="font-bold text-gray-300 mb-2 uppercase tracking-wider text-[10px]">Acceptance Criteria:</div>
             <div class="space-y-1.5">${{acceptanceChecks.map(c => `<div class="p-1.5 bg-gray-900 rounded font-mono text-[11px] text-gray-300">${{escapeHtml(c)}}</div>`).join('')}}</div>
           </div>`
        : '';

      bodyEl.innerHTML = `
        <div class="flex items-center justify-between pb-3 border-b border-[var(--border)]">
          <span class="text-gray-400">Owner: <strong class="text-blue-400">${{owner || 'Unassigned'}}</strong></span>
          ${{status ? getStatusBadge(status) : ''}}
        </div>
        <div>
          <div class="font-bold text-gray-300 mb-1 uppercase tracking-wider text-[10px]">Objective:</div>
          <p class="leading-relaxed text-gray-200 bg-gray-900/60 p-3 rounded-lg border border-[var(--border)]">${{objective || 'No objective specified.'}}</p>
        </div>
        ${{checksHtml}}
      `;
      document.getElementById('contract-modal').classList.remove('hidden');
    }}

    function closeModal() {{
      document.getElementById('contract-modal').classList.add('hidden');
    }}

    function escapeHtml(text) {{
      return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }}

    // Close modal on Escape
    window.addEventListener('keydown', e => {{
      if (e.key === 'Escape') closeModal();
    }});

    // Initial render
    renderList();
    renderDetail();
  </script>
</body>
</html>
"""
    return html


class WorkflowHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    repo_root: Path = REPO_ROOT

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            state = parse_work_directory(self.repo_root)
            html = generate_html_dashboard(state)
            encoded = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        elif self.path == "/api/workflow":
            state = parse_work_directory(self.repo_root)
            encoded = json.dumps(asdict(state), indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        elif self.path == "/health":
            body = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format: str, *args: Any) -> None:
        # Keep logs clean
        sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}\n")


def run_server(port: int = 8088, repo_root: Path = REPO_ROOT) -> None:
    handler = WorkflowHTTPRequestHandler
    handler.repo_root = repo_root
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🧶 Sulocraft Workflow GUI server running at http://localhost:{port}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sulocraft Workflow & Agent Coordination Dashboard")
    parser.add_argument("--build", nargs="?", const="work/dashboard.html", help="Build standalone HTML dashboard (default: work/dashboard.html)")
    parser.add_argument("--serve", action="store_true", help="Launch live HTTP server")
    parser.add_argument("--port", type=int, default=8088, help="Port for live HTTP server (default: 8088)")
    parser.add_argument("--json", action="store_true", help="Print parsed workflow state as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    state = parse_work_directory(REPO_ROOT)

    if args.json:
        print(json.dumps(asdict(state), indent=2))
        return 0

    if args.serve:
        run_server(port=args.port, repo_root=REPO_ROOT)
        return 0

    # Default or --build
    output_path = Path(args.build) if args.build else (WORK_DIR / "dashboard.html")
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    html = generate_html_dashboard(state)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Dashboard exported successfully to: {output_path}")
    print(f"Scanned {state.total_work_items} work items, {state.total_subtasks} subtasks ({state.overall_progress_percent}% overall progress).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
