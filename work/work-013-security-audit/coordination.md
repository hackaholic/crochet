# Security coordination

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

## Current handoffs

Task 13.11 (frontend source-map-js advisory & local audit test verification) is completed by Gemini; [security workflow run 38064775352](https://github.com/hackaholic/crochet/actions/runs/38064775352) passed all jobs including frontend audit and Master Security Release Gate. Task 13.10 is completed. Task 13.9 (VPS SSH deployment hardening) remains pending. Newly planned subtasks: [13.12 Schemathesis API fuzzing](tasks/task-012-schemathesis-api-fuzzing.md), [13.13 OWASP ZAP preprod DAST pipeline](tasks/task-013-zap-dast-preprod-pipeline.md), and [13.14 Authorization & business-logic matrix expansion](tasks/task-014-authorization-matrix-expansion.md).

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.
