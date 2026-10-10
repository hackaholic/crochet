# Shared coding skills

Skills root: `/home/anu/git/ai_skills`

Change only the root above if the shared folder moves. Resolve the paths below relative to that root.

| When needed | Skill entry point |
| --- | --- |
| Task design and dependencies | `architect/SKILL.md` |
| Implementation | `engineer/SKILL.md` |
| Test cases | `testcase-skill/SKILL.md` |
| Security checks | `security-validation/SKILL.md` |
| Review | `peer/SKILL.md` |
| Evidence-based skill improvements (approval required) | `skill-feedback/SKILL.md` |

Load only the relevant skill. Keep routine work to a short checklist with dependency readiness, test evidence, and security disposition for each subtask. Follow existing project security and release gates. If the root is unavailable, report it rather than guessing a replacement path.

## How Crochet uses the mapping

For a selected `work/` subtask, choose only the guidance needed at the current stage:

1. Resolve unclear design or dependencies with `architect`; define acceptance and security test cases with `testcase-skill` before implementation.
2. Implement with `engineer`, respecting the assigned owner and existing Gemini handoff rules.
3. Check relevant risks with `security-validation` and review the change with `peer`. Record evidence in the same task contract; label self-review accurately.
4. If actual work reveals a reusable improvement or repeated mistake, use `skill-feedback`. Show the proposed instruction change, evidence, expected benefit, risks, and validation plan. Wait for explicit user approval before changing any shared skill, including the feedback skill itself.

Example: a search API task reveals that its tests checked only HTTP status and missed unauthorized data in the response. Fix the task's tests within its authorized scope. If the shared testing guidance lacks this lesson, propose a minimal skill update and ask permission; if it already covers the lesson, follow it without adding duplicate instructions.

To try feedback explicitly: “Use $skill-feedback to review what we learned from this task. Propose an improvement only if the evidence supports one; ask before editing.” This mapping is agent guidance, not an automatic background process or a CI gate.
