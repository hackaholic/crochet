# Sulocraft — Project State & Persistent Task Management

> **Source of Truth**: This document is the canonical persistent task management and tracking record for the Sulocraft project.
> All agents (Gemini, Codex, etc.) must consult and update this file before and after executing work.

---

## 1. Project Objective
Build and launch **Sulocraft** (`sulocraft.com` / `dev.sulocraft.com`), a premium direct-to-consumer (D2C) e-commerce platform for handcrafted artisanal crochet products founded by Anupama Sharma.
The platform features:
- Artisanal storefront with database-driven merchandising, campaigns, categories, and seasonal occasions.
- High-conversion shopping flow: guest cart with auto-merge, checkout with address validation, multi-provider payment (Razorpay/Mock), order tracking, returns, and transactional notifications.
- Robust security & admin dashboard: role-based admin controls, date-bucketed sales/finance analytics, global search, and inventory management.
- Production-grade deployment: Docker Compose on VPS, SOPS/age secrets vault, Cloudflare Pages frontend, and Cloudflare R2 media CDN.

---

## 2. Key Architectural Decisions
- **Backend**: FastAPI with SQLAlchemy, PostgreSQL 17, Pydantic V2, Alembic migrations, UTC timestamps, `Asia/Kolkata` calendar business rules, integer paise for all monetary values.
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide icons, responsive mobile/desktop UI.
- **Data Persistence**: Strict separation of concerns — UI never hardcodes business data or inventory; all products, categories, collections, sections, and occasions are database-managed.
- **Authentication**: V1 global authentication with passwordless email magic links (Resend), Google/Facebook OAuth, HTTP-only SameSite session cookies. Phone numbers are strictly delivery contact data.
- **Secrets Management**: Host-only age private keys, service-scoped decrypted runtime files in `/run/sulocraft` with `umask 077`, fail-closed `<SETTING>_FILE` resolution.
- **Artwork & Media**: Relative R2 object keys persisted in DB; absolute URLs resolved dynamically via `IMAGE_BASE_URL` (`http://localhost:8000/static/images` locally, `https://images.sulocraft.com` in cloud). Strict duplicate-artwork guards.

---

## 3. Work Breakdown & Status Tracker

Status Legend:
- `Completed`: Verified with tests and live stack
- `In Progress`: Actively being implemented
- `Pending`: Ready to start or queued
- `Blocked`: Waiting on external dependency or owner input

---

### Work 001: Figma Admin Dashboard Integration
**Objective**: Integrate the owner-provided Figma admin export into the React storefront at `/admin`, connecting delivered backend APIs. Tracked in `work/work-001-admin-dashboard/`.

- [ ] **Task 1.1**: Figma admin export audit and component inventory per `tasks/task-001-screen-audit.md`. — `Pending`
- [ ] **Task 1.2**: Admin layout shell and route integration per `tasks/task-002-admin-layout-routes.md`. — `Pending`
- [ ] **Task 1.3**: Admin API client integration and state management per `tasks/task-003-api-integration.md`. — `Pending`
- [ ] **Task 1.4**: Admin UI automated tests and Docker verification per `tasks/task-004-ui-tests-verification.md`. — `Pending`

---

### Work 002: Product Gallery Media
**Objective**: Curate and upload distinct alternate views for all products and wire full image galleries. Tracked in `work/work-002-product-gallery-media/`.

- [ ] **Task 2.1**: Product gallery media audit per `tasks/task-001-media-audit.md`. — `Pending`
- [ ] **Task 2.2**: Curate and upload approved alternate product views per `tasks/task-002-curate-alternate-views.md`. — `Pending`
- [ ] **Task 2.3**: Catalogue seed and API media-key updates per `tasks/task-003-seed-api-updates.md`. — `Pending`
- [ ] **Task 2.4**: Local Docker storefront gallery verification per `tasks/task-004-local-docker-verification.md`. — `Pending`

---

### Work 003: SOPS/age Secret Vault
**Objective**: Transition from plaintext environment variables to SOPS/age service-scoped secrets vault for VPS deployment. Tracked in `work/work-003-vault/`.

- [x] **Task 3.1**: Compose secret interfaces per `tasks/task-001-compose-secrets.md`. — `Completed`
- [ ] **Task 3.2**: Local preprod decrypt helper per `tasks/task-002-local-preprod-decrypt.md`. — `Pending`
- [ ] **Task 3.3**: VPS secret bootstrap and deploy automation per `tasks/task-003-vps-deploy.md`. — `Pending`
- [ ] **Task 3.4**: Secret vault automated tests per `tasks/task-004-vault-tests.md`. — `Pending`
- [ ] **Task 3.5**: Local developer age key setup. — `Blocked` (Awaiting owner key permission fix)
- [ ] **Task 3.6**: Safe VPS key bootstrap automation per `tasks/task-005-vps-key-bootstrap.md`. — `Pending`
- [ ] **Task 3.7**: Guarded age key rotation automation per `tasks/task-006-age-key-rotation.md`. — `Pending`
- [ ] **Task 3.8**: Provision `.sops.yaml` rules and encrypt preprod groups per `tasks/task-007-sops-encryption.md`. — `Pending`
- [ ] **Task 3.9**: Repair seed issue, rebuild local Docker, and verify per `tasks/task-008-seed-repair-verification.md`. — `Pending`
- [ ] **Task 3.10**: Owner review and encrypted VPS release deployment per `tasks/task-009-vps-release.md`. — `Pending`

---

### Work 004: Agent Task Workflow
**Objective**: Standardize cross-agent task handoffs and the persistent `work/` folder workflow. Tracked in `work/work-004-task-workflow/`.

- [x] **Task 4.1**: Create `work/INDEX.md`, `TASK_TEMPLATE.md`, and dedicated work folders. — `Completed`
- [x] **Task 4.2**: Update project instructions and link contracts in `docs/handoffs.md`. — `Completed`
- [x] **Task 4.7**: Apply work-local coordination to all work items, archive detailed global logs, and provide Gemini's reusable workflow prompt. — `Completed`

---

### Work 005: Global SEO Optimization & Multinational Ranking
**Objective**: Implement multinational search engine optimization to rank high globally. Tracked in `work/work-005-seo-optimization/`.

- [ ] **Task 5.1**: Structured data and rich snippet validation per `tasks/task-001-structured-data.md`. — `Pending`
- [ ] **Task 5.2**: International SEO & hreflang architecture per `tasks/task-002-international-seo.md`. — `Pending`
- [ ] **Task 5.3**: Meta tags, dynamic social cards, and prerender route coverage per `tasks/task-003-meta-social-prerender.md`. — `Pending`
- [ ] **Task 5.4**: Automated SEO test suite and Core Web Vitals verification per `tasks/task-004-seo-audit-vitals.md`. — `Pending`

---

### Work 006: Preprod DNS, Email Deliverability & Continuous Deployment
**Objective**: Configure production DNS, authenticate email deliverability, and automate VPS CI/CD deployment. Tracked in `work/work-006-dns-email-cd/`.

- [ ] **Task 6.1**: Cloudflare & Resend DNS records configuration per `tasks/task-001-cloudflare-resend-dns.md`. — `Pending`
- [ ] **Task 6.2**: Transactional email deliverability and live provider verification per `tasks/task-002-email-deliverability.md`. — `Pending`
- [ ] **Task 6.3**: GitHub Actions CI/CD workflow hardening with protected secrets per `tasks/task-003-github-actions-cd.md`. — `Pending`
- [ ] **Task 6.4**: Cloudflare Pages dev storefront setup & Cloudflare Access per `tasks/task-004-dev-storefront-access.md`. — `Pending`

---

### Work 007: End-to-End Purchase & Mobile Rendering QA
**Objective**: Full customer journey QA across mobile and desktop viewport targets. Tracked in `work/work-007-e2e-qa/`.

- [ ] **Task 7.1**: Guest checkout & user login cart-merge regression per `tasks/task-001-guest-merge-regression.md`. — `Pending`
- [ ] **Task 7.2**: Multi-provider payment flow & webhook reconciliation testing per `tasks/task-002-payment-reconciliation.md`. — `Pending`
- [ ] **Task 7.3**: Mobile viewport rendering matrix verification per `tasks/task-003-mobile-rendering-matrix.md`. — `Pending`
- [ ] **Task 7.4**: Pre-launch quality sign-off and owner review per `tasks/task-004-prelaunch-signoff.md`. — `Pending`

---

### Work 008: Customer Promotions & Reviews Engine
**Objective**: Discount coupons engine and authenticated customer product reviews with moderation. Tracked in `work/work-008-promotions-reviews/`.

- [ ] **Task 8.1**: Promotions and coupons engine backend validation per `tasks/task-001-promotions-backend.md`. — `Pending`
- [ ] **Task 8.2**: Customer product review submission and moderation backend per `tasks/task-002-reviews-backend.md`. — `Pending`
- [ ] **Task 8.3**: Storefront coupon input & customer review UI integration per `tasks/task-003-promotions-reviews-ui.md`. — `Pending`
- [ ] **Task 8.4**: Promotions and reviews tests & local Docker verification per `tasks/task-004-tests-verification.md`. — `Pending`

---

### Work: Automated Security Audit & Release Gate
**Objective**: Build automated multi-level security audit workflow (Level 1 pre-push, Level 2 CI gate, Level 3 dev DAST). Tracked in `work/work-013-security-audit/`.

- [x] **Task 9.1**: Work directory structure, Threat Model, and Audit Policy per `tasks/task-001-threat-model-policy.md`. — `Completed`
- [x] **Task 9.2**: Secret scanning & secret architecture audit per `tasks/task-002-secrets-audit.md`. — `Completed`
- [x] **Task 9.3**: Static Application Security Testing (SAST) & dependency auditing per `tasks/task-003-sast-deps.md`. — `Completed`
- [x] **Task 9.4**: Container & infrastructure security scanning per `tasks/task-004-container-infra.md`. — `Completed`
- [x] **Task 9.5**: Custom backend authorization & e-commerce business logic tests per `tasks/task-005-auth-business-tests.md`. — `Completed`
- [x] **Task 9.6**: Dynamic security testing (DAST) & TLS auditing per `tasks/task-006-dast-tls.md`. — `Completed`
- [x] **Task 9.7**: Local pre-push security gate & master audit runner per `tasks/task-007-prepush-full-audit.md`. — `Completed`
- [x] **Task 9.8**: CI security workflow (.github/workflows/security.yml) per `tasks/task-008-ci-security-workflow.md`. — `Completed`

---

## 4. "Where are we?" Snapshot

| Dimension | Current State |
| :--- | :--- |
| **Current Focus** | Work: Automated Security Audit & Release Gate — All tasks 9.1–9.8 completed |
| **Last Completed Item** | Full release gate operational: Level 1 pre-push, Level 2 CI gate, Level 3 DAST/TLS |
| **Active Test Status** | Backend: **157/157 passed** (`pytest backend/tests/`)<br>Frontend: **48/48 passed** (`npm test`) |
| **Docker Stack** | Local stack running healthy on `http://localhost:8000` (API) and `http://localhost:8080` (Frontend) |
| **Release Gate** | **ELIGIBLE (PASS)** across all 10 security check dimensions |
| **Current Blockers** | None |
