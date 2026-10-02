# Work 003 tasks

## In Progress

None. Gemini's next task is 3.2; it has not been reported as started yet.

## Pending

- [ ] 3.2 Gemini: add [local preprod decrypt helper](tasks/task-002-local-preprod-decrypt.md) with ignored outputs and restrictive permissions.
- [ ] 3.3 Gemini: implement VPS secret bootstrap/deploy per [task-003-vps-deploy.md](tasks/task-003-vps-deploy.md).
- [ ] 3.4 Gemini: add tests per [task-004-vault-tests.md](tasks/task-004-vault-tests.md).
- [ ] 3.5 Owner + Codex: provision a local developer age key and make its private key readable only by the owner; publish only the public recipient.
- [ ] 3.6 Gemini: add [safe VPS key bootstrap automation](tasks/task-005-vps-key-bootstrap.md): create a root-only key only if absent, never overwrite, and output only the public recipient.
- [ ] 3.7 Gemini + Codex: add [guarded key rotation automation](tasks/task-006-age-key-rotation.md): stage a replacement key, re-encrypt/verify all groups, deploy successfully, then retire the old key only after owner confirmation.
- [ ] 3.8 Codex: add `.sops.yaml` rules and encrypt approved preprod groups after key setup.
- [ ] 3.9 Codex + Gemini: repair the unrelated duplicate seed issue, rebuild local Docker, and verify API/UI with dev secrets.
- [ ] 3.10 Owner + Codex: review the local result, then deploy encrypted dev configuration and verify API plus `https://dev.sulocraft.com`.

## Completed

- [x] 3.1 Gemini: implement [Compose secret interfaces](tasks/task-001-compose-secrets.md); implementation and 142 backend tests are recorded in `notes.md`.
- [x] Audit actual env names, Compose/deploy paths, and Git ignore rules.
- [x] Add generic `<SETTING>_FILE` handling and focused redaction/precedence tests.
- [x] Document the inventory, selected SOPS/age approach, and Gemini implementation contract.
- [x] Generate and verify the VPS age key as `root:root`, mode `0600`, with its directory at mode `0700`; only the public recipient was read.

## Blocked

- 3.5 Local key setup created an unreadable age-key file due to owner mapping. No encrypted files exist. Preserve it and repair owner permissions, or get explicit approval before replacing it.
- 3.9 Local API startup fails while seeding a duplicate product/occasion association; Gemini owns the seed repair.
- 3.10 The API is now healthy on the latest backend after an owner-requested direct `/opt/sulocraft` sync and Compose restart. The secure SOPS/age release is still blocked: runtime secret files were provisioned from the saved plaintext env for this manual deployment, and `/opt/sulocraft/current` still points at the prior release. Details are in `notes.md` and the Task 3.3 contract.
