# Exception EXC-001 — Use of xml.sax.saxutils.escape in Sitemap Serialization

- **Rule / CVE ID:** `python.lang.security.use-defused-xml.use-defused-xml`
- **Component:** `backend/app/services/seo.py:6`
- **Severity:** Medium (False Positive)
- **Date Approved:** 2026-10-02
- **Expiration Date:** 2026-12-01 (60 days)
- **Approved By:** Sulocraft Security Lead

## Technical Justification

Semgrep rule `use-defused-xml` warns against importing Python's standard `xml` library due to entity expansion (Billion Laughs) and external entity injection (XXE) risks during XML *parsing*.

In `backend/app/services/seo.py`, the only imported symbol is `from xml.sax.saxutils import escape as xml_escape`. This function is strictly used for outbound string entity encoding (escaping `&`, `<`, `>`, `"`) when constructing the XML sitemap response:
```python
loc_tag = f"  <url><loc>{xml_escape(url.loc)}</loc>..."
```
No XML parsing, document tree generation, or untrusted XML ingestion occurs anywhere in this service. Therefore, no XXE or entity expansion attack vector is possible.

## Temporary Mitigation

Code review confirmed the function only performs string character substitution on outbound data.

## Planned Resolution

Documented exception active in audit workflow.
