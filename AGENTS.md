# Project working rules

- Work and verify changes locally first. Rebuild or restart the affected Docker services, then inspect the actual storefront at `http://localhost:8080` and the API at `http://localhost:8000` when relevant.
- Confirm the changed behavior and its images/data render correctly in the local browser before pushing to `dev` or deploying to the VPS. Do not skip local verification.
- Add or update meaningful tests for every new feature or behavior change, and run the relevant checks before delivery.
- Keep storefront content and product data backend/database-driven. Do not hardcode business content into UI components; use reusable templates and render API data.
- Coordinate backend work with Gemini through `docs/handoffs.md`, `docs/coordination-status.md`, and `docs/TODO.md`. After Gemini completes backend work, verify the integrated Docker app locally before VPS deployment.
