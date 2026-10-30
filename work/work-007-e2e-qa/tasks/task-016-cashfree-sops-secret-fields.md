# Task 7.2.5 — Add Cashfree fields to the SOPS backend group

**Owner:** Codex  
**Status:** Completed

## Objective

Prepare the encrypted preprod backend secret group for Cashfree credentials so the owner only has to enter the App ID and Secret Key values.

## Context

The Cashfree backend adapter is complete under [7.2.3](task-015-cashfree-provider-api.md). The encrypted backend group exists at `secrets/encrypted/backend.enc.env`, but the SOPS decrypt helper does not yet allow Cashfree configuration keys. Keep secret values out of chat and logs.

## Scope

- In scope: allowlist Cashfree credential variables in the decrypt helper; load the App ID through the existing secret-file path; test writing each value to owner-only runtime files; add empty credential fields to the SOPS-encrypted backend group; document the credential group.
- Out of scope: entering credentials, running a payment, deployment, or production configuration.

## Dependencies and relevant files

- Depends on: [7.2.3](task-015-cashfree-provider-api.md)
- Dependency context: Gemini's Cashfree backend config expects provider/environment selection and reads credentials through the existing secret-file configuration.
- Blocked by: None
- Blocker reason: None
- Next action: Validate the encrypted-group edit and run focused secret helper tests.
- Inspect/edit: `scripts/decrypt_secrets.py`, `scripts/security/test_decrypt_secrets.py`, `secrets/encrypted/backend.enc.env`, `docs/secrets.md`

## Test cases

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 7.2.5-TC01 | Cashfree credentials are accepted from backend group | Success | Decrypt mocked backend group containing Cashfree credential fields | Each credential is written to its expected runtime file with mode `0600` | `python3 -m unittest scripts/security/test_decrypt_secrets.py` | Pass — 7 tests; private file mode asserted |
| 7.2.5-TC02 | Unknown secret names remain rejected | Security | Supply an unapproved backend key to the parser | Decryption fails closed without echoing its value | `python3 -m unittest scripts/security/test_decrypt_secrets.py` | Pass — negative case asserts secret value is not echoed |
| 7.2.5-TC03 | Encrypted group remains ciphertext | Security | SOPS decrypt/re-encrypt round-trip performed in memory; verify decrypted fields then suppress output | Existing values preserved; blank Cashfree credential fields included in revalidated ciphertext | Pinned SOPS image; no plaintext written or printed | Pass — round-trip integrity verified |

## Security validation

- Changed trust boundary: encrypted backend config becomes an input to local/VPS runtime secret materialization.
- Controls: strict key allowlist, SOPS age recipients, no plaintext credential values in the repo, runtime secret files remain mode `0600`, tests use fake credentials only.
- Commands/results: `python3 -m unittest scripts/security/test_decrypt_secrets.py` — 7 passed. Pinned SOPS container re-decrypted the candidate ciphertext in memory and verified all prior values plus the new empty fields; output suppressed.
- Disposition: Pass
- Findings/blockers: No credentials were entered. Container runtime wiring remains outside this field-preparation task.

## Acceptance checks

- [x] Cashfree keys are accepted by the backend secret-group allowlist.
- [x] The encrypted backend group contains `CASHFREE_APP_ID` and `CASHFREE_SECRET_KEY`; non-secret provider/environment settings stay in runtime config. The owner populated both credentials after this task, without recording values here.
- [x] Focused tests pass and runtime files are mode `0600`.
- [x] SOPS validation passes without exposing decrypted values.
- [x] Security disposition and exact evidence are recorded.

## Handoff back

Update Work 007 `tasks.md`, `notes.md`, and `coordination.md`. The owner has populated both fields through SOPS; do not request or record the values.
