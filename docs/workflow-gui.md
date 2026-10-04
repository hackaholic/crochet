# Sulocraft Workflow & Agent Coordination GUI

The Workflow GUI provides an interactive visual dashboard for browsing all work items (`work/work-*/`), tracking live subtask completion, inspecting cross-agent handoffs (Gemini, Codex, GPT, Owner), and reading detailed task specifications.

---

## 1. Quick Start / How to Run

### Method A: Docker Compose (Recommended)

Run the workflow dashboard in an isolated, lightweight container:

```bash
# Run standalone workflow GUI
docker-compose -f docker/compose.workflow.yaml up -d
```

Or run alongside the entire local stack (storefront, API, database, GUI):
```bash
docker-compose -f docker/compose.yaml up -d
```

Open your browser to: **`http://localhost:8088`**

> **Live Auto-Reloading:** The host's `work/` directory is mounted into the container as a read-only volume (`../work:/app/work:ro`). Any time you edit a `tasks.md`, check a box, or restart the container, the changes are immediately reflected on browser refresh without rebuilding the container!

To stop:
```bash
docker-compose -f docker/compose.workflow.yaml down
```

---

### Method B: Native Python Server

If you prefer running without Docker:

```bash
python3 scripts/workflow_gui.py --serve --port 8088
```

Open **`http://localhost:8088`**. Press `Ctrl+C` in your terminal to stop.

---

### Method C: Standalone Static HTML

Generate or view the single-file offline dashboard:

```bash
# Generate to work/dashboard.html
python3 scripts/workflow_gui.py --build
```

You can double-click `work/dashboard.html` or open it directly in any browser or IDE preview. It contains embedded data and requires zero network access or external dependencies.

---

### Method D: JSON Export

To inspect the raw parsed state programmatically:

```bash
python3 scripts/workflow_gui.py --json
```

---

## 2. How to Navigate the Dashboard

The interface is divided into an overview metrics bar and a two-column master-detail workspace:

```
┌────────────────────────────────────────────────────────────────────────┐
│  🧶 Sulocraft Workflow & Coordination   [Sync]  Progress: 66% (83/125) │
├────────────────────────────────────────────────────────────────────────┤
│  [All (14)]  [In Progress (4)]  [Completed (8)]  [Pending (2)]         │
│  [🔍 Search work, subtasks, agent...]                                  │
├───────────────────────────────────┬────────────────────────────────────┤
│  WORK ITEMS (List)                │  SELECTED ITEM DETAILS             │
│  ┌─────────────────────────────┐  │  Work 012 — VPS Isolation          │
│  │ #012 VPS Environment...     │  │  Owner: Codex | State: Deploy active│
│  │ [Completed] 10/11 (91%)     │  │  --------------------------------  │
│  └─────────────────────────────┘  │  Objective / Goal Summary          │
│  ┌─────────────────────────────┐  │  --------------------------------  │
│  │ #014 Task Progress GUI      │  │  ☑ Subtasks & Checklist            │
│  │ [Completed] 6/6 (100%)      │  │    ☑ 14.1.1 Structure              │
│  │                             │  │    ☑ 14.1.6 Docker service [View]  │
│  └─────────────────────────────┘  │  --------------------------------  │
│                                   │  📄 Task Contracts                 │
│                                   │  ⚖️ Recorded Decisions            │
└───────────────────────────────────┴────────────────────────────────────┘
```

### A. Top Metrics & Global Progress
- **Overall Progress Bar**: Shows the total project completion percentage calculated from all subtasks across all work items.
- **KPI Badges**: Quick overview of Total Items, Completed, In Progress, and Pending.
- **Sync Button**: Instantly re-scans the repository and reloads live data.

### B. Filtering & Search
- **Status Filter Pills**: Click `All`, `In Progress`, `Completed`, or `Pending` to filter the work list.
- **Real-Time Instant Search**: Type in the search box to filter instantly across:
  - Work item titles (e.g. `Isolation`, `Dashboard`, `Vault`)
  - Subtask names (e.g. `Docker`, `OAuth`, `Caddy`)
  - Agent assignees (e.g. `Gemini`, `Codex`, `Owner`)
  - Work IDs (e.g. `work-012`, `#003`)

### C. Left Column: Work Items List
- Displays cards for all 14 work items.
- Each card shows:
  - Item number and title
  - Status badge (Green = Completed, Blue = In Progress, Yellow = Pending)
  - Current assigned agent owner
  - Progress bar and completion ratio (e.g. `6/6 tasks (100%)`)
- **Clicking any card** selects it and populates the details on the right.

### D. Right Column: Work Item Detail Pane
When an item is selected, the right pane displays:
1. **Header**: Item title, ID, relative path in repository, and status badge.
2. **Objective / Goal**: The high-level business and technical objective from the item's `README.md`.
3. **Coordination & Handoff Card**:
   - **Current Owner**: Which agent is responsible (`Gemini`, `Codex`, `Owner`).
   - **Handoff State**: Current cross-agent handoff status.
4. **Subtasks & Checklist**:
   - Live checklist with `☑` (completed) and `☐` (pending) indicators.
   - Assignee tags (e.g. `Assigned: Gemini`).
   - **"View Contract" Button**: Present on subtasks that link to a formal task contract.
5. **Task Contracts Grid**: Quick access to all individual contracts under `tasks/*.md`.
6. **Recorded Decisions**: High-level architectural decisions from `decisions.md`.

### E. Task Contract Inspector (Modal)
- Clicking **"View Contract"** or any contract card opens an in-app reader modal.
- Displays:
  - Contract Title and Assignee
  - Full Objective and Context
  - Formal Acceptance Criteria / Checklist
- Press `Esc` or click `Close` to dismiss the modal.
