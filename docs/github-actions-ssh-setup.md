# GitHub Actions SSH Deployment Key Setup Guide

This guide documents how to create, configure, and authorize a dedicated SSH key pair on the VPS and configure GitHub Actions repository secrets for automated backend deployments to pre-production.

---

## 1. Key Architecture & Direction

> [!IMPORTANT]
> **Authentication Direction:**
> When the CI/CD workflow runs, **GitHub Actions is the SSH client** and the **VPS is the SSH server**.
>
> - **Public Key (`.pub`)** $\rightarrow$ Stays on the **VPS** in `~/.ssh/authorized_keys` (allows incoming logins).
> - **Private Key** $\rightarrow$ Added to **GitHub Repository Secrets** as `VPS_SSH_PRIVATE_KEY` (allows the runner to authenticate).
> - **DO NOT** add the VPS public key to your personal GitHub account SSH settings (`github.com/settings/keys`), as that only controls cloning repositories *from* the VPS.

---

## 2. Step-by-Step Configuration

### Step 1: Generate a Dedicated Deployment Key on the VPS

Log into your VPS terminal as `root` (or deployment user):

```bash
# Create .ssh directory if it does not exist with strict permissions
install -m 700 -d ~/.ssh

# Generate a modern Ed25519 key pair dedicated to GitHub Actions
ssh-keygen -t ed25519 -C "github-actions-sulocraft" -f ~/.ssh/github_actions_ed25519 -N ""
```

This creates two files:
- `~/.ssh/github_actions_ed25519` (Private key)
- `~/.ssh/github_actions_ed25519.pub` (Public key)

*(If you already ran `ssh-keygen` with the default name `id_ed25519`, use `~/.ssh/id_ed25519` and `~/.ssh/id_ed25519.pub` in the steps below).*

---

### Step 2: Authorize the Public Key on the VPS

Append the generated public key to `authorized_keys` so the VPS accepts logins using this key:

```bash
# Authorize the public key
cat ~/.ssh/github_actions_ed25519.pub >> ~/.ssh/authorized_keys

# Enforce secure Linux file permissions (required by sshd)
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_actions_ed25519
```

---

### Step 3: Get the Known Host Key (`VPS_KNOWN_HOSTS`)

To prevent SSH man-in-the-middle rejection without disabling host key verification, obtain the host key fingerprint:

```bash
ssh-keyscan -H 201.18.212.183
```

*Copy the printed output lines (they look like `|1|... ssh-ed25519 AAAAC3...`).*

---

### Step 4: Display the Private Key (`VPS_SSH_PRIVATE_KEY`)

Print the private key to copy it:

```bash
cat ~/.ssh/github_actions_ed25519
```

*Copy the **entire** block from `-----BEGIN OPENSSH PRIVATE KEY-----` down to `-----END OPENSSH PRIVATE KEY-----` (inclusive).*

---

### Step 5: Add Secrets to GitHub Repository Settings

1. Open your repository on GitHub in a web browser.
2. Navigate to: **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**.
3. Under **Repository secrets**, click **New repository secret** to add each of the following:

| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `VPS_SSH_PRIVATE_KEY` | Paste entire output from Step 4 (`cat ~/.ssh/github_actions_ed25519`) | Private key used by the runner to log in |
| `VPS_HOST` | `201.18.212.183` | The VPS public IP address |
| `VPS_USER` | `root` (or deployment user) | SSH login username |
| `VPS_KNOWN_HOSTS` | Paste output from Step 3 (`ssh-keyscan -H 201.18.212.183`) | Pinned SSH host key line |

> [!NOTE]
> **No Plaintext Environment File Needed:**
> You do **not** need to create a `PREPROD_ENV_FILE` secret. Sulocraft uses SOPS-encrypted configuration tracked in Git under `secrets/encrypted/`. The deployment script decrypts configuration on the VPS using the server's local age key (`/etc/sulocraft/age/keys.txt`).

---

## 3. Workflow Trigger & Verification

Once secrets are configured:

1. Push a commit affecting `backend/**` to the `dev` branch:
   ```bash
   git push origin dev
   ```
2. Or trigger manually via GitHub Actions:
   - Go to **Actions** tab $\rightarrow$ **Deploy development backend** $\rightarrow$ **Run workflow** (select `dev` branch).
3. The workflow will:
   - Check out code and run backend tests (`pytest`) with `uv`.
   - On test success, configure SSH keys securely in runner memory (`~/.ssh/id_ed25519` with `0600` mode).
   - Execute `backend/scripts/deploy_vps.sh --env preprod --host "${VPS_USER}@${VPS_HOST}"`.
   - Backup database, bootstrap secrets via age, start Compose project `sulocraft-preprod`, and verify health.

---

## 4. Troubleshooting & Common Pitfalls

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `Permission denied (publickey)` | Public key not added to VPS `~/.ssh/authorized_keys` or wrong file permissions | Check `~/.ssh/authorized_keys` contains the `.pub` content and permissions are `0700` for `~/.ssh` and `0600` for `authorized_keys`. |
| `Host key verification failed` | Missing or incorrect `VPS_KNOWN_HOSTS` | Re-run `ssh-keyscan -H 201.18.212.183` and update the `VPS_KNOWN_HOSTS` secret. |
| `Load key ...: invalid format` | Truncated or malformed private key | Ensure the entire key including `-----BEGIN...` and `-----END...` lines with exact newlines was pasted into `VPS_SSH_PRIVATE_KEY`. |
| Added public key to GitHub account | Misunderstanding of authentication direction | Personal GitHub SSH keys do not permit inbound SSH to VPS. The public key must go into VPS `~/.ssh/authorized_keys`, and the private key into GitHub Actions Repository Secrets. |

---

## 5. Security Hardening: Restricting SSH Key (Defense-in-Depth)

To break the "Secret Zero" chicken-and-egg vulnerability where an SSH key compromise could expose the server, apply these hardening controls:

### A. Restrict Key Capabilities in `authorized_keys`
You can prefix the public key in `~/.ssh/authorized_keys` with SSH options that disable interactive terminals, port forwarding, and X11 forwarding:

```text
no-pty,no-port-forwarding,no-agent-forwarding,no-X11-forwarding ssh-ed25519 AAAAC3NzaC1yc2E... github-actions-sulocraft
```

- `no-pty`: Prevents an attacker from allocating a pseudo-terminal (cannot open an interactive bash shell).
- `no-port-forwarding`: Blocks tunneling traffic into internal VPS ports (e.g., cannot tunnel to PostgreSQL on 5432).

### B. Dedicated Non-Root Deploy User
In production:
1. Create a dedicated system user: `adduser --system --group --shell /bin/bash deploy`.
2. Add the public key to `/home/deploy/.ssh/authorized_keys`.
3. Set ownership of `/etc/sulocraft/age/keys.txt` to `root:root` mode `0600`. The `deploy` user cannot read the Age private key directly.
4. Allow `deploy` sudo access only for Docker commands or the deploy script via `/etc/sudoers.d/deploy`:
   ```text
   deploy ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/local/bin/docker-compose
   ```
5. Set `VPS_USER=deploy` in GitHub Secrets.

With these controls, even if the private SSH key in GitHub is leaked, an attacker cannot open a shell, cannot browse root files, and cannot read the server's Age decryption keys.
