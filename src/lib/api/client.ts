const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? '';

/** VITE_API_BASE_URL must include the version prefix, e.g. https://api.sulocraft.com/api/v1. */
export function apiUrl(path: string): string {
  if (!configuredBaseUrl) return `/api/v1${path}`;
  return `${configuredBaseUrl}${path}`;
}
