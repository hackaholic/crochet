# Task 13.9 — VPS deployment SSH key hardening, capability restriction & least-privilege runner isolation

**Owner:** Pending
**Status:** Pending
**Work item:** Work 013 (Automated Security Audit & Hardening)

## Objective

Harden the GitHub Actions SSH deployment pathway on the VPS to resolve the "Secret Zero" threat vector: ensure that an exposure of the deployment SSH key cannot grant an attacker an interactive root shell, arbitrary command execution, internal network tunneling, or direct access to the server's master Age decryption key (`/etc/sulocraft/age/keys.txt`).

## Context and contract

Sulocraft uses SOPS + Age to encrypt credentials at rest in Git, decrypting them in memory on the VPS during deployment. Because GitHub Actions holds an SSH private key (`VPS_SSH_PRIVATE_KEY`) to trigger deployment, that SSH key must be hardened through defense-in-depth so that its potential compromise does not grant unrestricted host control.

Relevant reference:
- [`docs/github-actions-ssh-setup.md`](../../../docs/github-actions-ssh-setup.md)
- [`docs/secrets.md`](../../../docs/secrets.md)
- [`work/work-013-security-audit/threat-model.md`](../threat-model.md)

## Scope

- In scope:
  - Documenting and implementing SSH key capability restrictions (`no-pty`, `no-port-forwarding`, `no-agent-forwarding`, `no-X11-forwarding`) in `~/.ssh/authorized_keys`.
  - Creating a dedicated non-root `deploy` user with scoped sudo permissions for Docker/Compose operations.
  - Ensuring `/etc/sulocraft/age/keys.txt` remains unreadable by non-root users (`0600`, `root:root`).
  - Evaluating and testing forced command wrappers (`command="/opt/sulocraft/scripts/deploy-wrapper"`) to reject arbitrary shell execution.
  - Adding automated security audit checks to ensure SSH permissions and configurations remain compliant.
- Out of scope:
  - Modifying live VPS configuration without explicit owner authorization.
  - Replacing the core SOPS/Age architecture.

## Subtasks

- [ ] **13.9.1 — SSH Capability Restriction**:
  - Restrict the deployment public key in `authorized_keys` with `no-pty,no-port-forwarding,no-agent-forwarding,no-X11-forwarding`.
  - Verify interactive shell (`ssh -t`) and TCP forwarding are blocked while batch deployment commands succeed.
- [ ] **13.9.2 — Dedicated Non-Root `deploy` System User**:
  - Provision `deploy` user with `/home/deploy/.ssh/authorized_keys`.
  - Ensure `/etc/sulocraft/age/keys.txt` is owned by `root:root` with mode `0600`, inaccessible to `deploy`.
  - Configure `/etc/sudoers.d/deploy` for least-privilege command execution only (Docker and Compose).
- [ ] **13.9.3 — Forced Command / Wrapper Enforcement**:
  - Define an SSH wrapper or `command="..."` directive that restricts inbound SSH connections to the deployment script, rejecting arbitrary commands or directory traversals.
- [ ] **13.9.4 — Security Audit Verification**:
  - Add an automated check in `scripts/security/scan-config.sh` verifying that deployment SSH keys enforce capability restrictions and that the Age key maintains strict `0600` root-only ownership.

## Acceptance checks

- [ ] Deployment SSH key cannot allocate a pseudo-terminal or establish port forwarding.
- [ ] Non-root `deploy` account cannot read `/etc/sulocraft/age/keys.txt`.
- [ ] Automated security scan passes and validates that no unencrypted keys or unrestricted deployment identities exist.
- [ ] CI deployment workflow `.github/workflows/deploy-dev-backend.yml` functions seamlessly with the hardened deployment user and restricted key.

## Handoff back

- Update `work/work-013-security-audit/tasks.md` and `notes.md`.
- Coordinate with Work 006 (CI/CD) and Work 012 (VPS Isolation).
