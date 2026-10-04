# Sulocraft Threat Model

## 1. System Overview & Architecture

Sulocraft is a direct-to-consumer (D2C) artisanal e-commerce platform consisting of:
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, pre-rendered with Node.js and hosted on Cloudflare Pages / Caddy reverse proxy.
- **Backend API**: Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic V2, PostgreSQL 17.
- **Storage & Assets**: Cloudflare R2 object storage for product images and encrypted backups.
- **Third-Party Integrations**: Razorpay (payments & webhooks), Resend (transactional email magic links), Fast2SMS/Twilio (order updates), Google/Facebook (OAuth).
- **Secrets Management**: SOPS + age encryption with service-scoped files under `/run/sulocraft/`.

---

## 2. Threat Actors & Motivations

| Threat Actor | Motivation | Capabilities |
| :--- | :--- | :--- |
| **Anonymous Web Attacker** | Data theft, disruption, unauthorized discounts | Probing public APIs, automated vulnerability scanning, inventory hoarding |
| **Malicious Authenticated Customer** | Financial fraud, free goods, identity theft | IDOR attacks on other customers' orders/addresses, price/quantity tampering |
| **Malicious Insider / Compromised Dev** | Credential theft, unauthorized access | Leaking credentials in commits, modifying build pipelines |
| **Compromised Dependency (Supply Chain)** | Code execution, backdoor injection | Malicious npm/PyPI updates containing vulnerabilities |
| **Network Eavesdropper (MitM)** | Session hijacking, payment tampering | Intercepting unencrypted traffic, forging webhook payloads |

---

## 3. High-Value Assets

1. **Customer PII**: Delivery addresses, phone numbers, recipient names, gift messages, order histories.
2. **Financial Transactions**: Order amounts, payment verification signatures, refund authorizations.
3. **Platform Credentials**: PostgreSQL credentials, Cloudflare R2 access keys, Resend API key, Razorpay secret keys, OAuth client secrets, age private keys.
4. **Catalogue & Stock Data**: Inventory allocations, wholesale pricing, admin operational metrics.
5. **Administrative Controls**: Order cancellation, shipment status updates, customer role management.

---

## 4. Threat Scenarios & Defensive Mitigations

### 4.1 Broken Object Level Authorization (IDOR)
- **Threat**: Customer A inspects `GET /api/v1/orders/{order_id}` and modifies `{order_id}` to access Customer B's order.
- **Impact**: Exposure of Customer B's delivery address, phone number, and purchase details.
- **Mitigation**: All database queries for orders, addresses, and returns must strictly filter by `Order.customer_id == current_user.id` unless the requester possesses verified `admin` role. Returns 404/403 on mismatch.

### 4.2 E-Commerce Business Logic & Price Tampering
- **Threat**: Attacker sends a manipulated payload during checkout with `unit_price: 1`, `discount_amount: 99999`, or negative quantities (`quantity: -5`).
- **Impact**: Revenue loss, free merchandise, negative order subtotals.
- **Mitigation**: The backend strictly ignores client-submitted prices, taxes, discounts, and subtotals. It recalculates authoritative integer paise totals directly from the database catalog and valid coupon tables. Pydantic models enforce `quantity >= 1`.

### 4.3 Credential Leaks in Source & Images
- **Threat**: Accidental commit of API keys, `.env` files, or embedding age keys in Docker images.
- **Impact**: Full compromise of database, email sender reputation, or cloud storage.
- **Mitigation**: Level 1 Gitleaks pre-push scanning; Level 2 CI secret scan; SOPS/age encrypted groups; service-scoped secret mounts; zero image layer secrets.

### 4.4 Injection Attacks (SQLi, Command, XSS)
- **Threat**: Malicious input in search strings, review text, or occasion filters attempting SQL injection or stored XSS.
- **Impact**: Database exfiltration or browser script execution.
- **Mitigation**: Strict parameterized queries via SQLAlchemy ORM (forbidding raw string concatenation); React automatic escaping; Semgrep SAST security rules in CI.

### 4.5 Broken Authentication & Magic Link Replay
- **Threat**: Interception of magic links, reuse of tokens, or forging OAuth callbacks.
- **Impact**: Account takeover.
- **Mitigation**: Cryptographically secure, single-use magic link tokens with 15-minute expiration; atomic consumption; OAuth state validation; verified-email linking only.

### 4.6 Docker & Infrastructure Exposure
- **Threat**: Exposing PostgreSQL port 5432 to the public internet, mounting the Docker socket, or running containers as root.
- **Impact**: VPS host compromise.
- **Mitigation**: PostgreSQL port 5432 bound exclusively to Docker internal network; Trivy container audits; non-root user execution in production containers.

### 4.7 CI/CD Deployment SSH Key Exposure & "Secret Zero"
- **Threat**: The deployment SSH private key stored in GitHub Actions (`VPS_SSH_PRIVATE_KEY`) is exfiltrated or abused to gain access to the VPS.
- **Impact**: Attacker attempts to obtain an interactive root shell, execute arbitrary commands, read `/etc/sulocraft/age/keys.txt`, or tunnel into private Docker networks.
- **Mitigation**: Defense-in-depth via SSH capability restrictions (`no-pty`, `no-port-forwarding`, `no-agent-forwarding`, `no-X11-forwarding`), dedicated non-root `deploy` user with root-only Age key permissions (`0600`), and restricted command wrappers (`command="..."`). See Task 13.9.
