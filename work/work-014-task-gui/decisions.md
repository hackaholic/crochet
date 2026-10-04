# Work 014 decisions

## DEC-014-01: Zero External Runtime Dependencies

- **Context**: The project needs a lightweight, cross-platform way to visualize work items and task progress without adding heavy npm/pip runtime dependencies.
- **Decision**: Implement the parser and HTTP server using Python's standard library (`http.server`, `urllib`, `re`, `json`, `pathlib`). The frontend dashboard is rendered as an embedded single-page application using vanilla JavaScript and the allowlisted GStatic Tailwind CSS CDN (`https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js`).
- **Consequence**: Anyone with Python 3 can run `python3 scripts/workflow_gui.py --serve` without installing packages. The dashboard can also be built as a self-contained static HTML file.

## DEC-014-02: Live Read directly from Repository Markdown Files

- **Context**: As tasks transition between Pending, In Progress, and Completed across different agents (Gemini, Codex, GPT), hardcoding state in a database or JSON cache risks becoming stale.
- **Decision**: The dashboard parser directly reads `work/INDEX.md`, each work folder's `tasks.md`, `coordination.md`, and individual task files in `tasks/*.md` on demand. In server mode (`--serve`), each page refresh re-reads the filesystem, ensuring instant real-time parity with Git.
