/** Shared UI request budgets; prevents an unbounded or stalled discovery stream. */
export const discoveryLimits = { maxPages: 40, timeoutMs: 8000 } as const;
