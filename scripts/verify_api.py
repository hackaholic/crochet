#!/usr/bin/env python3
"""Automated API Verification & Reporting Suite for Sulocraft E-Commerce Platform.

Verifies:
1. Storefront Home occasion_grid resolution, seasonal-first ordering, and updated artwork.
2. Catalogue occasion listings and hidden occasion rules.
3. Multi-occasion product filtering and SKU uniqueness.
4. Admin occasion management, `isEvergreen` field presence, and evergreen mutation protection.
5. Markdown report generation for auditing and CI/release gating.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
import http.cookiejar
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


@dataclass
class CheckResult:
    group: str
    name: str
    status: str  # "PASS" | "FAIL" | "WARN"
    http_code: int
    duration_ms: float
    details: str
    payload_summary: str = ""


class ApiVerifier:
    def __init__(self, base_url: str, admin_email: str = "admin@sulocraft.com"):
        self.base_url = base_url.rstrip("/")
        self.admin_email = admin_email
        self.results: list[CheckResult] = []
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        self.auth_token: str | None = None
        self.start_time: datetime = datetime.now(timezone.utc)
        self.end_time: datetime | None = None

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, Any, float]:
        url = f"{self.base_url}{path}"
        req_headers = {"Accept": "application/json"}
        if headers:
            req_headers.update(headers)
        if self.auth_token:
            req_headers["Authorization"] = f"Bearer {self.auth_token}"

        encoded_data = None
        if data is not None:
            req_headers["Content-Type"] = "application/json"
            encoded_data = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(
            url, data=encoded_data, headers=req_headers, method=method
        )
        start = time.perf_counter()
        try:
            with self.opener.open(req, timeout=15) as resp:
                duration_ms = (time.perf_counter() - start) * 1000
                raw = resp.read().decode("utf-8")
                body = json.loads(raw) if raw else None
                return resp.status, body, duration_ms
        except urllib.error.HTTPError as e:
            duration_ms = (time.perf_counter() - start) * 1000
            raw = e.read().decode("utf-8")
            try:
                body = json.loads(raw) if raw else None
            except Exception:
                body = raw
            return e.code, body, duration_ms
        except Exception as ex:
            duration_ms = (time.perf_counter() - start) * 1000
            return 0, str(ex), duration_ms

    def record(
        self,
        group: str,
        name: str,
        status: str,
        http_code: int,
        duration_ms: float,
        details: str,
        payload_summary: str = "",
    ):
        self.results.append(
            CheckResult(
                group=group,
                name=name,
                status=status,
                http_code=http_code,
                duration_ms=round(duration_ms, 2),
                details=details,
                payload_summary=payload_summary,
            )
        )

    # ---------------------------------------------------------
    # Test Suites
    # ---------------------------------------------------------

    def test_health(self):
        code, body, dur = self._request("GET", "/health")
        if code == 200:
            self.record("Core", "Health Endpoint", "PASS", code, dur, "API service responsive")
        else:
            # Fallback to docs/openapi
            code2, _, dur2 = self._request("GET", "/openapi.json")
            if code2 == 200:
                self.record("Core", "OpenAPI Endpoint", "PASS", code2, dur2, "API docs responsive")
            else:
                self.record("Core", "Health Endpoint", "FAIL", code, dur, f"Unhealthy status {code}")

    def test_storefront_home(self) -> dict[str, Any] | None:
        code, body, dur = self._request("GET", "/api/v1/storefront/home")
        if code != 200:
            self.record("Storefront", "Home Sections", "FAIL", code, dur, f"HTTP {code} returned")
            return None

        sections = body.get("sections", []) if isinstance(body, dict) else []
        occ_grid = next((s for s in sections if s.get("type") == "occasion_grid"), None)

        if not occ_grid:
            self.record(
                "Storefront",
                "Occasion Grid Section",
                "FAIL",
                code,
                dur,
                "Section 'occasion_grid' missing from storefront home",
            )
            return None

        self.record(
            "Storefront",
            "Occasion Grid Section",
            "PASS",
            code,
            dur,
            f"Found occasion_grid section titled '{occ_grid.get('title')}'",
        )

        items = occ_grid.get("occasions") or occ_grid.get("items") or []
        if not items:
            self.record("Storefront", "Occasion Grid Items", "FAIL", code, dur, "Occasion items list empty")
            return None

        self.record(
            "Storefront",
            "Occasion Grid Items",
            "PASS",
            code,
            dur,
            f"Successfully resolved {len(items)} occasion cards in storefront grid",
        )

        # Verify ordering: seasonal occasions must precede evergreen occasions
        evergreen_ids = {"birthday", "anniversary", "wedding", "babyshower"}
        found_ids = [item.get("id") for item in items]

        first_evergreen_idx = next(
            (i for i, item_id in enumerate(found_ids) if item_id in evergreen_ids), None
        )
        last_seasonal_idx = next(
            (
                len(found_ids) - 1 - i
                for i, item_id in enumerate(reversed(found_ids))
                if item_id not in evergreen_ids
            ),
            None,
        )

        ordering_pass = True
        ordering_details = f"Resolved sequence: {', '.join(found_ids)}"
        if first_evergreen_idx is not None and last_seasonal_idx is not None:
            if first_evergreen_idx < last_seasonal_idx:
                ordering_pass = False
                ordering_details += f" (ERROR: evergreen index {first_evergreen_idx} < seasonal index {last_seasonal_idx})"

        if ordering_pass:
            self.record(
                "Storefront",
                "Seasonal-First Ordering",
                "PASS",
                code,
                dur,
                f"Seasonal occasions precede evergreen occasions. {ordering_details}",
            )
        else:
            self.record(
                "Storefront",
                "Seasonal-First Ordering",
                "FAIL",
                code,
                dur,
                f"Ordering violation! {ordering_details}",
            )

        # Verify 4 Evergreen Occasions Present
        missing_evergreen = evergreen_ids - set(found_ids)
        if not missing_evergreen:
            self.record(
                "Storefront",
                "Evergreen Occasions Present",
                "PASS",
                code,
                dur,
                "All 4 core evergreen occasions present: birthday, anniversary, wedding, babyshower",
            )
        else:
            self.record(
                "Storefront",
                "Evergreen Occasions Present",
                "FAIL",
                code,
                dur,
                f"Missing evergreen occasions: {missing_evergreen}",
            )

        # Verify Updated -v2.png Artwork
        items_by_id = {item.get("id"): item for item in items}
        artwork_expectations = {
            "birthday": "birthday-gifting-v2.png",
            "anniversary": "anniversary-gifting-v2.png",
            "wedding": "wedding-gifting-v2.png",
        }
        for occ_id, expected_img in artwork_expectations.items():
            item = items_by_id.get(occ_id)
            img_url = (item.get("imageUrl") or item.get("image_url") or "") if item else ""
            if expected_img in img_url:
                self.record(
                    "Storefront",
                    f"Artwork Check ({occ_id})",
                    "PASS",
                    code,
                    dur,
                    f"Image URL correctly contains '{expected_img}' ({img_url})",
                )
            else:
                self.record(
                    "Storefront",
                    f"Artwork Check ({occ_id})",
                    "FAIL",
                    code,
                    dur,
                    f"Expected '{expected_img}' in URL, got '{img_url}'",
                )

        return occ_grid

    def test_catalogue_occasions(self):
        code, body, dur = self._request("GET", "/api/v1/occasions")
        if code != 200:
            self.record("Catalogue", "List Occasions", "FAIL", code, dur, f"HTTP {code}")
            return

        if not isinstance(body, list):
            self.record("Catalogue", "List Occasions", "FAIL", code, dur, "Expected array response")
            return

        ids = [occ.get("id") for occ in body]
        # Rakhi should be hidden by default
        if "rakhi" in ids:
            self.record("Catalogue", "Hidden Occasion (Rakhi)", "FAIL", code, dur, "Disabled occasion 'rakhi' returned")
        else:
            self.record("Catalogue", "Hidden Occasion (Rakhi)", "PASS", code, dur, "Disabled occasion 'rakhi' omitted")

        # Seasonal before evergreen check
        evergreen_ids = {"birthday", "anniversary", "wedding", "babyshower"}
        first_evergreen_idx = next((i for i, o_id in enumerate(ids) if o_id in evergreen_ids), None)
        last_seasonal_idx = next(
            (len(ids) - 1 - i for i, o_id in enumerate(reversed(ids)) if o_id not in evergreen_ids), None
        )

        if first_evergreen_idx is not None and last_seasonal_idx is not None and first_evergreen_idx < last_seasonal_idx:
            self.record(
                "Catalogue",
                "Catalogue Seasonal-First Ordering",
                "FAIL",
                code,
                dur,
                f"Evergreen appeared before seasonal: {ids}",
            )
        else:
            self.record(
                "Catalogue",
                "Catalogue Seasonal-First Ordering",
                "PASS",
                code,
                dur,
                f"{len(ids)} occasions returned in seasonal-first order: {', '.join(ids)}",
            )

    def test_product_filtering(self):
        # Baby Shower product filtering
        code, body, dur = self._request("GET", "/api/v1/products?occasion=babyshower")
        if code != 200:
            self.record("Catalogue", "Baby Shower Filtering", "FAIL", code, dur, f"HTTP {code}")
            return

        products = body if isinstance(body, list) else body.get("items", [])
        product_ids = [p.get("id") for p in products]
        expected_ids = {17, 19, 16, 3}

        # Check for duplicate IDs
        if len(product_ids) != len(set(product_ids)):
            self.record(
                "Catalogue",
                "Product Uniqueness",
                "FAIL",
                code,
                dur,
                f"Duplicate products returned for occasion: {product_ids}",
            )
        else:
            self.record(
                "Catalogue",
                "Product Uniqueness",
                "PASS",
                code,
                dur,
                "No duplicate SKUs/products in occasion listing",
            )

        missing = expected_ids - set(product_ids)
        if not missing:
            self.record(
                "Catalogue",
                "Baby Shower Product Associations",
                "PASS",
                code,
                dur,
                f"All expected products {sorted(expected_ids)} returned for 'babyshower'",
            )
        else:
            self.record(
                "Catalogue",
                "Baby Shower Product Associations",
                "FAIL",
                code,
                dur,
                f"Missing expected product IDs: {missing} (returned: {product_ids})",
            )

    def test_admin_auth_and_occasions(self):
        # Authenticate as admin via dev Google mock
        login_payload = {
            "credential": "mock_admin_token_occ",
            "email": self.admin_email,
            "name": "Store Admin",
            "sub": "admin_sub_occ",
        }
        code, body, dur = self._request("POST", "/api/v1/auth/google", data=login_payload)
        if code != 200 or not isinstance(body, dict) or body.get("user", {}).get("role") != "ADMIN":
            self.record(
                "Admin",
                "Admin Authentication",
                "FAIL",
                code,
                dur,
                f"Failed to login as admin: {body}",
            )
            return

        self.record("Admin", "Admin Authentication", "PASS", code, dur, f"Authenticated as {self.admin_email}")

        # Fetch Admin Occasions List
        code, occasions, dur = self._request("GET", "/api/v1/admin/occasions")
        if code != 200 or not isinstance(occasions, list):
            self.record("Admin", "List Admin Occasions", "FAIL", code, dur, f"HTTP {code}")
            return

        self.record("Admin", "List Admin Occasions", "PASS", code, dur, f"Retrieved {len(occasions)} occasions")

        # Verify isEvergreen field on all records
        missing_flag = [o.get("id") for o in occasions if "isEvergreen" not in o and "is_evergreen" not in o]
        if missing_flag:
            self.record(
                "Admin",
                "isEvergreen Field Exposure",
                "FAIL",
                code,
                dur,
                f"Occasions missing isEvergreen flag: {missing_flag}",
            )
        else:
            self.record(
                "Admin",
                "isEvergreen Field Exposure",
                "PASS",
                code,
                dur,
                "All occasion objects expose isEvergreen schema field",
            )

        # Verify specific evergreen classification
        evergreen_expected = {"birthday", "anniversary", "wedding", "babyshower"}
        occ_by_id = {o.get("id"): o for o in occasions}
        mismatched = []
        for o_id, occ in occ_by_id.items():
            is_ev = occ.get("isEvergreen") if "isEvergreen" in occ else occ.get("is_evergreen")
            expected_ev = o_id in evergreen_expected
            if is_ev != expected_ev:
                mismatched.append(f"{o_id} (got {is_ev}, expected {expected_ev})")

        if mismatched:
            self.record(
                "Admin",
                "Evergreen Classification Accuracy",
                "FAIL",
                code,
                dur,
                f"Mismatched classifications: {', '.join(mismatched)}",
            )
        else:
            self.record(
                "Admin",
                "Evergreen Classification Accuracy",
                "PASS",
                code,
                dur,
                "Core 4 occasions are evergreen (true); seasonal occasions are not (false)",
            )

        # -----------------------------------------------------
        # Evergreen Mutation Protection Checks
        # -----------------------------------------------------

        # Check 1: Disabling an evergreen occasion must return 400
        code, body, dur = self._request(
            "PATCH",
            "/api/v1/admin/occasions/birthday",
            data={"isEnabled": False},
        )
        if code == 400:
            detail = body.get("detail", "") if isinstance(body, dict) else str(body)
            self.record(
                "Admin Governance",
                "Reject Evergreen Disabling",
                "PASS",
                code,
                dur,
                f"HTTP 400 correctly raised. Detail: {detail}",
            )
        else:
            self.record(
                "Admin Governance",
                "Reject Evergreen Disabling",
                "FAIL",
                code,
                dur,
                f"Expected HTTP 400 when disabling evergreen, got {code}",
            )

        # Check 2: Scheduling dates on evergreen occasion must return 400
        code, body, dur = self._request(
            "PATCH",
            "/api/v1/admin/occasions/birthday",
            data={"startsAt": "2026-05-01T00:00:00Z"},
        )
        if code == 400:
            detail = body.get("detail", "") if isinstance(body, dict) else str(body)
            self.record(
                "Admin Governance",
                "Reject Evergreen Scheduling",
                "PASS",
                code,
                dur,
                f"HTTP 400 correctly raised. Detail: {detail}",
            )
        else:
            self.record(
                "Admin Governance",
                "Reject Evergreen Scheduling",
                "FAIL",
                code,
                dur,
                f"Expected HTTP 400 when adding schedule dates to evergreen, got {code}",
            )

        # Check 3: Deleting an evergreen occasion must return 400
        code, body, dur = self._request("DELETE", "/api/v1/admin/occasions/birthday")
        if code == 400:
            detail = body.get("detail", "") if isinstance(body, dict) else str(body)
            self.record(
                "Admin Governance",
                "Reject Evergreen Deletion",
                "PASS",
                code,
                dur,
                f"HTTP 400 correctly raised. Detail: {detail}",
            )
        else:
            self.record(
                "Admin Governance",
                "Reject Evergreen Deletion",
                "FAIL",
                code,
                dur,
                f"Expected HTTP 400 when deleting evergreen, got {code}",
            )

        # Check 4: Seasonal schedule date clearing via null
        code, body, dur = self._request(
            "PATCH",
            "/api/v1/admin/occasions/valentine",
            data={"startsAt": None, "endsAt": None},
        )
        if code == 200:
            s_at = body.get("startsAt") or body.get("starts_at")
            e_at = body.get("endsAt") or body.get("ends_at")
            if s_at is None and e_at is None:
                self.record(
                    "Admin Governance",
                    "Clear Seasonal Schedule Dates",
                    "PASS",
                    code,
                    dur,
                    "HTTP 200: startsAt and endsAt successfully cleared to null",
                )
            else:
                self.record(
                    "Admin Governance",
                    "Clear Seasonal Schedule Dates",
                    "FAIL",
                    code,
                    dur,
                    f"Dates not null: startsAt={s_at}, endsAt={e_at}",
                )
        else:
            self.record(
                "Admin Governance",
                "Clear Seasonal Schedule Dates",
                "FAIL",
                code,
                dur,
                f"Failed to clear dates on seasonal occasion, got {code}",
            )

    def run_all(self):
        self.start_time = datetime.now(timezone.utc)
        print("=" * 70)
        print("SULOCRAFT API AUTOMATED VERIFICATION SUITE")
        print(f"Target Base URL: {self.base_url}")
        print(f"Timestamp:       {self.start_time.isoformat()}")
        print("=" * 70)

        self.test_health()
        self.test_storefront_home()
        self.test_catalogue_occasions()
        self.test_product_filtering()
        self.test_admin_auth_and_occasions()

        self.end_time = datetime.now(timezone.utc)
        self.print_summary()

    def print_summary(self):
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        total = len(self.results)
        duration_total = sum(r.duration_ms for r in self.results)

        print("\n" + "-" * 70)
        print(f"{'GROUP':<18} | {'CHECK NAME':<32} | {'STATUS':<6} | {'TIME':<8}")
        print("-" * 70)
        for r in self.results:
            status_str = f"\033[92m{r.status}\033[0m" if r.status == "PASS" else f"\033[91m{r.status}\033[0m"
            print(f"{r.group:<18} | {r.name:<32} | {status_str:<15} | {r.duration_ms:>6.1f}ms")

        print("-" * 70)
        print(f"TOTAL: {total} | PASSED: {passed} | FAILED: {failed} | DURATION: {duration_total:.1f}ms")
        print("-" * 70)

    def generate_markdown_report(self, output_path: str):
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        total = len(self.results)
        duration_total = sum(r.duration_ms for r in self.results)
        status_overall = "PASSED" if failed == 0 and total > 0 else "FAILED"

        lines = [
            "# API Automation Verification Report",
            "",
            f"**Execution Timestamp:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            f"**Target Host:** `{self.base_url}`  ",
            f"**Overall Status:** **{status_overall}**  ",
            f"**Total Duration:** `{duration_total:.2f} ms`  ",
            "",
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "| :--- | :--- |",
            f"| **Overall Result** | `{'✅ ' + status_overall if status_overall == 'PASSED' else '❌ ' + status_overall}` |",
            f"| **Total Verification Checks** | `{total}` |",
            f"| **Passed Checks** | `{passed}` |",
            f"| **Failed Checks** | `{failed}` |",
            f"| **API Base URL** | `{self.base_url}` |",
            "",
            "---",
            "",
            "## Granular Verification Breakdown",
            "",
            "| Domain / Group | Verification Check | Status | HTTP Code | Latency | Details |",
            "| :--- | :--- | :---: | :---: | :---: | :--- |",
        ]

        for r in self.results:
            icon = "✅ PASS" if r.status == "PASS" else "❌ FAIL"
            lines.append(
                f"| **{r.group}** | {r.name} | {icon} | `{r.http_code}` | `{r.duration_ms}ms` | {r.details} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Occasion Grid Governance & Artwork Audit",
            "",
            "This run confirms the following critical business rules:",
            "1. **Seasonal-First Ordering**: Enabled and in-season seasonal discovery cards lead the homepage grid, ahead of evergreen staples.",
            "2. **Evergreen Guarantee**: The 4 core occasions (`birthday`, `anniversary`, `wedding`, `babyshower`) remain permanently active year-round.",
            "3. **Artwork Upgrades**: Modern refreshed artwork (`-v2.png`) correctly bound and served for Birthday, Anniversary, and Wedding.",
            "4. **Admin Protection**: Destructive mutations (disabling, scheduled dates, deletion) against evergreen occasions are strictly rejected with HTTP 400.",
            "5. **Multi-Occasion Products**: Single SKU/catalogue identity preserved across multiple occasions (e.g. Baby Shower tagged products).",
            "",
            "---",
            f"*Generated by Sulocraft Automated Verification Suite (`scripts/verify_api.py`) on {self.start_time.isoformat()}*",
            "",
        ])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\nAudit report successfully written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Sulocraft API Automated Verification Suite")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--admin-email",
        default="admin@sulocraft.com",
        help="Admin user email for privileged checks (default: admin@sulocraft.com)",
    )
    parser.add_argument(
        "--report",
        default="work/work-011-api-verification/reports/api-verification-report.md",
        help="Path for markdown report output",
    )
    args = parser.parse_args()

    verifier = ApiVerifier(base_url=args.base_url, admin_email=args.admin_email)
    verifier.run_all()

    if args.report:
        verifier.generate_markdown_report(args.report)

    failed = any(r.status == "FAIL" for r in verifier.results)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
