"""Schemathesis OpenAPI Property-Based Contract & Fuzz Testing.

Conforms to Work 013 Task 13.12 (task-012-schemathesis-api-fuzzing.md).
Automatically scans all FastAPI endpoints from /openapi.json using in-process ASGI
transport, ensuring zero 500 crashes, schema conformance, and auth bypass detection.
"""

from hypothesis import HealthCheck, Phase, settings
import schemathesis
from schemathesis.checks import (
    content_type_conformance,
    not_a_server_error,
    status_code_conformance,
)

from app.main import app

# Load OpenAPI schema directly from in-process ASGI FastAPI app
schema = schemathesis.openapi.from_asgi("/openapi.json", app)


@schema.include(path_regex=r"^(/health|/api/v1/(storefront|catalogue|search))").parametrize()
@settings(
    max_examples=5,
    phases=[Phase.generate],
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    deadline=None,
)
def test_public_routes_fuzzing_and_conformance(case: schemathesis.Case):
    """13.12-TC01 & 13.12-TC02: Public endpoints must conform to schema and never crash with 500."""
    response = case.call(timeout=30)
    case.validate_response(
        response,
        checks=(
            not_a_server_error,
            status_code_conformance,
            content_type_conformance,
        ),
    )


@schema.include(path_regex=r"^/api/v1/cart").parametrize()
@settings(
    max_examples=5,
    phases=[Phase.generate],
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    deadline=None,
)
def test_cart_routes_fuzzing_no_server_errors(case: schemathesis.Case):
    """13.12-TC01: Cart endpoints handle fuzzed boundary payloads safely without 500 errors."""
    response = case.call(timeout=30)
    assert response.status_code < 500, (
        f"Server crash on {case.method} {case.formatted_path}: status {response.status_code}"
    )
    case.validate_response(
        response,
        checks=(
            not_a_server_error,
        ),
    )


@schema.include(path_regex=r"^/api/v1/(admin|orders|account)").parametrize()
@settings(
    max_examples=3,
    phases=[Phase.generate],
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    deadline=None,
)
def test_protected_routes_auth_enforcement_and_no_bypass(case: schemathesis.Case):
    """13.12-TC03: Protected endpoints reject unauthorized/fuzzed requests; no 200 auth bypass or 500 crashes."""
    response = case.call(timeout=30)
    # Unauthenticated / fuzzed requests to protected routes must be rejected (400, 401, 403, 404, or 422)
    assert response.status_code in {400, 401, 403, 404, 422}, (
        f"Auth bypass or unexpected code on {case.method} {case.formatted_path}: returned {response.status_code}"
    )
    case.validate_response(
        response,
        checks=(
            not_a_server_error,
        ),
    )
