# Decisions

DEC-025-001: Local media uses root-relative URLs through the storefront proxy instead of a particular machine IP. Configuration only distinguishes local media base from deployed CDN base; same generic application resolver supports both. Proxy uses fixed configured upstream, never client-supplied destination. Preserve traversal guards and CORS; do not rewrite arbitrary external media.
