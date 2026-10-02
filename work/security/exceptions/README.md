# Security Exceptions

This directory stores approved, time-bound security exceptions for accepted risks or upstream unpatched vulnerabilities.

### Exception Template:
```markdown
# Exception EXC-<ID> — <Title>

- **Rule / CVE ID:** <e.g. CVE-2024-XXXXX or Semgrep rule>
- **Component:** <Package or file>
- **Severity:** High / Medium
- **Date Approved:** YYYY-MM-DD
- **Expiration Date:** YYYY-MM-DD (max 60 days)
- **Approved By:** <Owner>

## Technical Justification
<Detailed explanation why the vulnerability is not exploitable in the Sulocraft runtime architecture>

## Temporary Mitigation
<Compensating controls in place>

## Planned Resolution
<Upstream patch tracking or replacement plan>
```
