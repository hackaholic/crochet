import React from 'react';

interface CountryFlagProps {
  countryCode?: string | null;
  className?: string;
  title?: string;
}

/**
 * Validates ISO 3166-1 alpha-2 country code.
 * Excludes 'UNKNOWN' or arbitrary invalid codes.
 */
export function isValidIsoCountryCode(code?: string | null): code is string {
  if (!code || typeof code !== 'string') return false;
  const trimmed = code.trim().toUpperCase();
  if (trimmed.length !== 2) return false;
  return /^[A-Z]{2}$/.test(trimmed) && trimmed !== 'UN' && trimmed !== 'ZZ';
}

/**
 * Converts a 2-letter ISO country code into Unicode Regional Indicator Symbols (emoji flag).
 */
export function getCountryFlagEmoji(code: string): string {
  const upper = code.trim().toUpperCase();
  const codePoints = [...upper].map(char => 127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

/**
 * Renders an ISO flag emoji if valid, or a neutral SVG globe fallback for unknown/invalid country codes.
 * Accessible with role="img" and an aria-label.
 */
export default function CountryFlag({ countryCode, className = 'inline-block mr-1.5', title }: CountryFlagProps) {
  const valid = isValidIsoCountryCode(countryCode);

  if (valid) {
    const flag = getCountryFlagEmoji(countryCode);
    return (
      <span
        role="img"
        aria-label={title || `Flag for ${countryCode.toUpperCase()}`}
        className={`select-none text-base leading-none ${className}`}
        data-testid="country-flag-emoji"
      >
        {flag}
      </span>
    );
  }

  // Neutral globe fallback for UNKNOWN or invalid codes
  return (
    <span
      role="img"
      aria-label={title || 'Unknown destination'}
      className={`select-none inline-flex items-center justify-center text-[#9C8B7E] ${className}`}
      data-testid="country-flag-fallback"
    >
      <svg
        className="w-4 h-4 fill-none stroke-current"
        viewBox="0 0 24 24"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="10" />
        <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
        <path d="M2 12h20" />
      </svg>
    </span>
  );
}
