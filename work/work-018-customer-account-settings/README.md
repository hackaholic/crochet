# Work 018 — Customer profile, addresses and order experience

**Owner:** Codex (work lead)
**Status:** In Progress

## Objective
Provide a usable customer account with validated editable contact data, managed addresses, and order details with honest shipment progress. Use the supplied 2026-10-10 profile/settings screenshots as layout references while retaining Sulocraft styling and only relevant commerce menus.

## Current state
Profile/Addresses/Orders navigation, validated contact/address editing, safe errors/retries, order items and API milestones are implemented.18.5 completed. Local account/API acceptance passes;18.6 remains blocked by Firefox browser availability and Work01717.5 guest-link acceptance. Task18.12 clickable overview cards is implemented and tests pass, but authenticated desktop/mobile browser review is blocked by the local demo-account magic-link cooldown. Task18.13 confirms email and Google server-session logout in tests, but the user's reported runtime issue remains blocked pending exact environment/page reproduction. Local QA fixtures are retained for review only; no push/deployment.

## Scope and dependencies
Reuse existing auth/account/address/order APIs and Work017 tracking components. Backend-first contracts 18.2/18.3/18.4 enable UI task18.5. Work017 final acceptance remains separate. No carrier integration, password settings, social-profile fields, subscriptions or invented data. Same implementation in all environments.

## Definition of done
Backend contracts returned with tests/security evidence; validated accessible Profile/Addresses/Orders views implemented; real local API and desktop/mobile browser checks pass; Chrome and Firefox checks recorded (explicit blocker if unavailable). No push until user accepts the local result.

## Modules
Frontend: reusable src/components/account/ editors/navigation/order views; API transport in src/lib/api/; shared validation utilities. Backend: existing schemas/routes delegating new business rules to focused account/order services. Reuse ShipmentTracking and OrderTrackingPanel rather than another tracking implementation.
