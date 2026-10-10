# Gemini repository workflow prompt

Use these rules for every Sulocraft task and retain them in your project context. The repository is the source of truth; chat messages supplement the recorded task but do not replace it.

## Before starting

1. Read `work/INDEX.md`.
2. Read only the selected work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and the exact task contract linked in the assignment. Read relevant code and API contracts only.
3. Confirm the assigned task ID, objective, scope, dependencies, and acceptance checks. Do not begin a task that is not assigned to you or already owned by another agent. Ask the owner if the contract is ambiguous or conflicts with the code.
4. Mark only your assigned checklist item and contract **In Progress** in that work folder. Update its `coordination.md` to show Gemini as owner and the handoff as Active.

## While working

- **Environment parity applies to every project task:** develop production-grade behavior in pre-production. Keep the same application code/artifact, service architecture, deployment workflow, and security controls across preprod and production. Promotion should require configuration and environment-specific secrets only. Do not add preprod-only code paths or manual deployment procedures; select environment-specific hosts, domains, paths, and encrypted secret groups through validated config/env/CLI inputs. Fail closed if production configuration is missing and never fall back to preprod secrets.
- **Every release follows three gates:** local implementation plus relevant tests and browser/API verification must pass before preprod deployment; preprod must then be exercised and stable before production promotion; production uses the same tested revision/artifact with only environment configuration and secrets changed. Do not skip phases or deploy unverified working-tree changes.

- Keep the assigned task's scope. Add newly discovered work to the same work's `tasks.md`, or propose a separate work item if it is a distinct objective; do not silently expand the contract.
- Keep backend catalogue, occasion, homepage, search, and campaign content database-driven. Do not invent frontend behavior, data, or arbitrary HTML when an API/schema change is needed.
- Do not repeat completed work. Treat exact paths, R2 object keys, URLs, uploads, and verified setup listed as completed in the task contract as existing inputs. If R2 upload is complete, update the DB/seed/migration references only unless the contract explicitly asks you to replace the asset.
- Never use stock/Unsplash images when the contract calls for Sulocraft-owned or approved artwork.
- Add or update meaningful tests for changed behavior. Run the focused checks available in the project container and report exact commands/results; distinguish tests you ran from checks you could not run.
- Do not put credentials, private keys, access tokens, or secret values in code, logs, task notes, or handoffs.
- Do not push, deploy, sync to the VPS, or modify external services unless that exact action is explicitly assigned and authorized. Codex owns integrated local verification and combined release unless the owner changes this rule.

## Returning the task

1. Update the exact contract and work-local `tasks.md` status. Mark the Gemini implementation portion complete only when its acceptance checks are satisfied; otherwise leave it In Progress or Blocked with the concrete reason.
2. Update that work's `notes.md` with concise changed files, schema/migration/data effects, test commands/results, and remaining integration risks. Update `coordination.md` to **Returned** or **Blocked**, link the task contract, and say exactly what Codex/owner should do next.
3. Do not paste a second copy of the contract or detailed implementation report into global docs. Keep `docs/handoffs.md` as a short link registry; keep `docs/coordination-status.md` as a router to the work index and active registry.
4. Send the owner a concise report naming the Work ID, task ID, status, test results, and next action. Make no claim that local integrated acceptance passed unless it was actually run.

## Handoff contract format

Every cross-agent task must use `work/TASK_TEMPLATE.md` and live under `work/<work-folder>/tasks/`. The work folder is the single source of truth for scope, decisions, status, blockers, and return handoff. One task per handoff; do not hand over a whole work item unless the contract explicitly defines a bounded set of subtasks.

## Contract filename convention

Use `task-NNN-description.md`: a three-digit file number and lowercase hyphenated description. Preserve existing valid filenames and logical task IDs inside contracts/checklists; the filename number is not a dotted subtask ID. Allocate an unused number within the containing `tasks/` directory. Never delete completed contracts or renumber existing files to close gaps. When renaming a nonconforming file, preserve its content/status/ownership and update every reference, including coordination and handoff indexes.
