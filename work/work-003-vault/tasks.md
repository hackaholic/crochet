# Work 003 tasks

## In Progress

None.

## Pending

- Work 003 does not own VPS deployment. The deployment automation and environment isolation are tracked in [Work 012](../vps-environment-isolation/README.md).

## Completed

- [x] 3.13 Gemini: [isolate backend tests from shared development databases](tasks/task-013-isolate-backend-test-database.md); added fail-closed DB guards, dynamic entity cleanup in `backend/tests/conftest.py`, disposable test compose service `docker/compose.test.yaml`, and `backend/scripts/run_isolated_tests.sh`. Full suite (173/173 tests) passing with 0 failures and preprod DB protected.
- [x] 3.9 Codex + Gemini: [rebuild local Docker and verify API/UI](tasks/task-008-seed-repair-verification.md) with dev secrets and verified seed idempotency.
- [x] 3.2 Codex: local decrypt helper and Compose secret overlay integrated; focused decryption tests, local API health, storefront data, and image endpoint verified.
- [x] 3.1 Gemini: implement [Compose secret interfaces](tasks/task-001-compose-secrets.md); implementation and 142 backend tests are recorded in `notes.md`.
- [x] 3.14 Gemini: [make vault deployment environment-configurable](tasks/task-014-configurable-deployment-environments.md); added dynamic `scripts/decrypt_secrets.py`, `--env` and `--config` CLI options, strict fail-closed cross-env isolation, and updated bootstrap/deploy scripts.
- [x] 3.11 Gemini: fix [idempotent catalogue seed associations](tasks/task-011-seed-idempotency.md); centralized `seed_product_occasions` helper, eliminated duplicate loops, and added isolated/repeated regression tests.
- [x] 3.3 Gemini: implement VPS secret bootstrap/deploy per [task-003-vps-deploy.md](tasks/task-003-vps-deploy.md); created `backend/scripts/bootstrap_secrets.sh` and updated `backend/scripts/deploy_vps.sh` for encrypted SOPS deployment.
- [x] 3.4 Gemini: add tests per [task-004-vault-tests.md](tasks/task-004-vault-tests.md); 6 regression tests in `backend/tests/test_vault_deploy.py` (14/14 vault & secret tests pass).
- [x] 3.6 Gemini: add [safe VPS key bootstrap automation](tasks/task-005-vps-key-bootstrap.md); created `backend/scripts/bootstrap_vps_key.sh` with fail-closed key refusal and ephemeral container execution.
- [x] 3.7 Gemini + Codex: add [guarded key rotation automation](tasks/task-006-age-key-rotation.md); created `backend/scripts/rotate_vps_key.sh` supporting candidate key staging, promotion with active backup, and rollback.
- [x] 3.8 Codex: configure SOPS recipients and encrypt approved preprod secret groups in [Task 3.8 contract](tasks/task-007-sops-encryption.md).
- [x] 3.12 Codex: fix SOPS dotenv parsing, migration secret-file precedence, and rotation Docker fallback in [Task 3.12 contract](tasks/task-012-dotenv-runtime-integration.md).
- [x] Audit actual env names, Compose/deploy paths, and Git ignore rules.
- [x] Add generic `<SETTING>_FILE` handling and focused redaction/precedence tests.
- [x] Document the inventory, selected SOPS/age approach, and Gemini implementation contract.
- [x] Generate and verify the VPS age key as `root:root`, mode `0600`, with its directory at mode `0700`; only the public recipient was read.
- [x] 3.5 Owner + Codex: restored the existing local key to `anu:anu` mode `0600` and verified its public recipient using a temporary container. Private key material was not exposed.

## Blocked

None. All Work 003 tasks are completed.
