# Decisions
- DEC022-1: Discover incrementally from normal task logs; no whole-repository scan required.
- DEC022-2: Fix underlying API/compatibility issues, not global warning suppression. Any unavoidable third-party warning exception needs precise category/source, reason, owner and review condition.
- DEC022-3: Avoid duplicate work with Gemini's active test repairs. Reuse already delivered fixes; no implementation until file ownership confirmed.
- DEC022-4: Each new warning gets an unused task-NNN-description.md contract with evidence and focused tests; completed tasks are retained.
